import asyncio
import glob
import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, Form, BackgroundTasks
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseModel
from starlette.requests import Request

from subtaitles.core import translate_srt
from subtaitles.exceptions import AppError
from subtaitles.locale import L, LocaleKey
from subtaitles.translate import Engine, LANG

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
locale = L.get("cs")  # todo: middleware


class TranslationRequest(BaseModel):
    id: str
    subtitles: list[str]
    status: str = "pending"


MEMORY: dict[str, TranslationRequest] = {}
EXCEPTIONS: dict[str, Exception] = {}


async def process_async(req_id: str, path: str, engine: Engine):
    try:
        logger.info(f"translating: {path} using {engine}")
        res_path = await translate_srt(Path(path), engine, LANG.EN, LANG.CS)
        MEMORY.get(req_id).status = "done"
        logger.info(f"translated: {path} using {engine}")
        MEMORY.get(req_id).path = res_path
    except Exception as e:
        logger.exception(f"Error while translating: {path} using {engine}")
        MEMORY.get(req_id).status = "error"
        EXCEPTIONS[req_id] = e


def process(req_id: str, path: str, engine: Engine):
    asyncio.run(process_async(req_id, path, engine))


@app.exception_handler(AppError)
def show_error(request, err: AppError):
    error_message = err.render(locale)
    # error_message = getattr(err, "detail", str(err))
    context = {
        "request": request,
        "error": error_message,
        "locale": locale,
        "latest": [item for item in MEMORY.values()][:10],
    }
    RedirectResponse(request)
    return templates.TemplateResponse("home.html", context)


@app.exception_handler(Exception)
def show_error(request, err: Exception):
    error_message = getattr(err, "detail", str(err))
    context = {
        "request": request,
        "error": error_message,
        "locale": locale,
        "latest": [item for item in MEMORY.values()][:10],
    }
    RedirectResponse(request)
    return templates.TemplateResponse("error.html", context)


class Storage:

    base_path = os.environ.get("SUBTAITLES_STORAGE", "/tmp/subtaitles")

    # FileOnDisk = Tuple[str, str]

    def create(self, filename: str, content: str, lang: str = None) -> TranslationRequest:
        filename, ext = filename.rsplit(".", 1)

        if ext != "srt":
            raise AppError(LocaleKey.ONLY_SRT, extension=ext)

        req_id = str(uuid4())[-8:]

        if lang:
            filename = f"translated-{filename}.{lang}.{ext}"
        else:
            filename = f"{filename}.{ext}"

        path = os.path.join(self.base_path, req_id, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        logger.info(f"Storing to {path!r}")
        with open(path, "w") as fp:
            fp.write(content)

        return TranslationRequest(id=req_id, subtitles=[path])

    def list(self, latest_count: int = None) -> list[TranslationRequest]:
        # items = os.listdir(self.base_path)
        items = glob.glob(os.path.join(self.base_path, "*"))
        items.sort(key=os.path.getctime)

        if latest_count:
            items = items[:latest_count]

        result = []
        for item in items:
            content = os.listdir(os.path.join(self.base_path, item))
            status = "done" if len(content) > 1 else "error"
            if srts := [c for c in content if c.endswith(".srt")]:
                result.append(
                    TranslationRequest(
                        id=os.path.basename(item),
                        subtitles=srts,
                        status=status,
                    )
                )

        return result

    def read(self, req_id: str, lang: str = None) -> str | None:
        content = None
        subfolder = os.listdir(os.path.join(self.base_path, req_id))
        if srt := [c for c in subfolder if c.endswith(".srt")]:

            if lang:
                srt = [s for s in srt if s.startswith(f"translated-{lang}")]
                if not srt:
                    raise AppError(LocaleKey.TRANSLATED_NOT_FOUND, language=lang)

            with open(os.path.join(self.base_path, req_id, srt[0]), "r") as fp:
                content = fp.read()

        return content


def load_from_storage(storage_backend: Storage):
    global MEMORY
    MEMORY = {}
    for item in storage_backend.list(latest_count=999):
        MEMORY[item.id] = item


storage = Storage()
load_from_storage(storage)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "locale": locale,
            "latest": [item for item in MEMORY.values()][:10],
        }
    )


@app.post("/translate")
async def translate(file: UploadFile, background_tasks: BackgroundTasks, engine: str = Form()):
    if not file or not file.filename:
        # detail=f"No file uploaded"
        raise AppError()

    _, ext = file.filename.rsplit(".", 1)
    if ext != "srt":
        # detail=locale.ONLY_SRT.format(f".{ext}")
        raise AppError()

    logger.info(f"storing: {file.filename}, {file.size}")
    content = (await file.read()).decode(encoding="utf-8")
    t_req = storage.create(file.filename, content)
    MEMORY[t_req.id] = t_req

    logger.info(f"submitting: {t_req.id}")
    background_tasks.add_task(process, t_req.id, t_req.subtitles[0], engine=Engine(engine))

    return RedirectResponse(f"/translations/{t_req.id}", status_code=303, headers=None, background=None)


@app.get("/translations/{translation_id}")
async def detail(request: Request, translation_id):
    item: TranslationRequest = MEMORY.get(translation_id)

    if not item:
        raise AppError(LocaleKey.NOT_FOUND, translation_id=translation_id)

    # if exc := EXCEPTIONS.get(item.id):
    #     raise exc

    context = {
        "title": locale.TITLE,
        "new_upload": locale.NEW_UPLOAD,
        "request": request,
        "id": translation_id,
        "item": item,
        "processing": item.status == 'pending',
        "locale": locale,

    }
    return templates.TemplateResponse("processing.html", context)


@app.get("/translations/{translation_id}/download")
async def download(translation_id, response_class=FileResponse):
    item: TranslationRequest = MEMORY.get(translation_id)

    if not item:
        raise AppError(locale_key=locale.NOT_FOUND, translation_id=translation_id)

    if exc := EXCEPTIONS.get(item.id):
        raise exc

    return FileResponse(item.path)


@app.get("/api/translations/{translation_id}/status")
async def translations_status(translation_id):
    item: TranslationRequest = MEMORY.get(translation_id)
    return {
        "status": item.status if item else None
    }


@app.get("/api/translations")
async def translations_list() -> list[TranslationRequest]:
    return [item for item in MEMORY.values()]


app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
