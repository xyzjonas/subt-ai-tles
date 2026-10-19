from fastapi import APIRouter, FastAPI

router = APIRouter(prefix="/api")


@router.get("/hello")
def hello() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}


app = FastAPI(title="subt-ai-tles")
app.include_router(router)
