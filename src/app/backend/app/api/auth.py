from fastapi import APIRouter, status

from app.db import DbDep
from app.schemas import PasswordChange, ProfileUpdate, UserOut
from app.security import AuthenticatedUser
from app.services import users

router = APIRouter(prefix="/auth", tags=["auth"])


# These accept a user who still has to change their temporary password.
@router.get("/me")
def me(user: AuthenticatedUser) -> UserOut:
    return UserOut.model_validate(user)


@router.patch("/me")
def update_me(body: ProfileUpdate, db: DbDep, user: AuthenticatedUser) -> UserOut:
    return UserOut.model_validate(users.set_locale(db, user, body.locale))


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(body: PasswordChange, db: DbDep, user: AuthenticatedUser) -> None:
    users.change_password(db, user, body.current_password, body.new_password)
