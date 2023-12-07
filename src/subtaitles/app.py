import asyncio
import os
from typing import Tuple
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, UploadFile, Form, BackgroundTasks
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseModel
from starlette.requests import Request

from subtaitles.locale import L
from subtaitles.core import translate_srt
from subtaitles.translate import Engine, LANG

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
locale = L.get("cs")  # todo: middleware


class ProcessingEntry(BaseModel):
    id: str
    path: str
    status: str


MEMORY: dict[str, ProcessingEntry] = {}
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


class AppError(Exception):

    def __init__(self, detail: str, *args):
        super().__init__(str, *args)
        self.detail = detail


@app.exception_handler(Exception)
def show_error(request, err: Exception):
    error_message = getattr(err, "detail", str(err))
    context = {
        "request": request,
        "error": error_message,
        "locale": locale,
    }
    return templates.TemplateResponse("error.html", context)


class Storage:

    base_path = os.environ.get("SUBTAITLES_STORAGE", "/tmp/subtaitles")

    FileOnDisk = Tuple[str, str]

    def save(self, filename: str, content: str, lang: str = None) -> FileOnDisk:
        _, ext = filename.rsplit(".", 1)

        if ext != "srt":
            raise AppError(detail=locale.ONLY_SRT.format(ext))

        req_id = str(uuid4())[-8:]

        if lang:
            filename = f"translated-{lang}-{filename}"

        path = os.path.join(self.base_path, req_id, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        logger.info(f"Storing to {path!r}")
        with open(path, "w") as fp:
            fp.write(content)

        return req_id, path

    def list(self) -> list[FileOnDisk]:
        items = os.listdir(self.base_path)

        result = []
        for item in items:
            content = os.listdir(os.path.join(self.base_path, item))
            if srt := [c for c in content if c.endswith(".srt")]:
                result.append((item, srt[0]))

        return result

    def read(self, req_id: str, lang: str = None) -> str | None:
        content = None
        subfolder = os.listdir(os.path.join(self.base_path, req_id))
        if srt := [c for c in subfolder if c.endswith(".srt")]:

            if lang:
                srt = [s for s in srt if s.startswith(f"translated-{lang}")]
                if not srt:
                    raise AppError(f"Translated subtitles ({lang}) not found.")

            with open(os.path.join(self.base_path, req_id, srt[0]), "r") as fp:
                content = fp.read()

        return content


storage = Storage()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "locale": locale})


@app.post("/translate")
async def translate(file: UploadFile, background_tasks: BackgroundTasks, engine: str = Form()):
    if not file or not file.filename:
        raise AppError(detail=f"No file uploaded")

    _, ext = file.filename.rsplit(".", 1)
    if ext != "srt":
        raise AppError(detail=locale.ONLY_SRT.format(f".{ext}"))

    logger.info(f"storing: {file.filename}, {file.size}")
    content = (await file.read()).decode(encoding="utf-8")
    req_id, path = storage.save(file.filename, content)
    MEMORY[req_id] = ProcessingEntry(id=req_id, path=path, status="processing")

    logger.info(f"submitting: {req_id}")
    background_tasks.add_task(process, req_id, path, engine=Engine(engine))

    return RedirectResponse(f"/processes/{req_id}", status_code=303, headers=None, background=None)


@app.get("/processes/{process_id}")
async def detail(request: Request, process_id):
    item: ProcessingEntry = MEMORY.get(process_id)

    if not item:
        raise AppError(detail=locale.NOT_FOUND.format(process_id))

    if exc := EXCEPTIONS.get(item.id):
        raise exc

    context = {
        "title": locale.TITLE,
        "new_upload": locale.NEW_UPLOAD,
        "request": request,
        "id": process_id,
        "item": item,
        "processing": item.status == 'processing',
        "locale": locale,

    }
    return templates.TemplateResponse("processing.html", context)


@app.get("/processes/{process_id}/download")
async def download(process_id, response_class=FileResponse):
    item: ProcessingEntry = MEMORY.get(process_id)

    if not item:
        raise AppError(detail=locale.NOT_FOUND.format(process_id))

    if exc := EXCEPTIONS.get(item.id):
        raise exc

    return FileResponse(item.path)


@app.get("/processes/{process_id}/status")
async def detail(process_id):
    item: ProcessingEntry = MEMORY.get(process_id)
    return {
        "status": item.status if item else None
    }


app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
