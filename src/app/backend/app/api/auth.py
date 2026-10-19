from fastapi import APIRouter

from app.schemas import UserOut
from app.security import CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
