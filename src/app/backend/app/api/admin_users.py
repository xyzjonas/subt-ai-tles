from fastapi import APIRouter, Depends, status

from app.db import DbDep
from app.schemas import UserCreate, UserOut, UserUpdate
from app.security import AdminUser, require_admin
from app.services import users

router = APIRouter(
    prefix="/admin/users", tags=["admin"], dependencies=[Depends(require_admin)]
)


@router.get("")
def list_users(db: DbDep) -> list[UserOut]:
    return [UserOut.model_validate(user) for user in users.list_all(db)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: DbDep) -> UserOut:
    return UserOut.model_validate(users.create(db, body))


@router.get("/{user_id}")
def get_user(user_id: int, db: DbDep) -> UserOut:
    return UserOut.model_validate(users.get(db, user_id))


@router.patch("/{user_id}")
def update_user(user_id: int, body: UserUpdate, db: DbDep) -> UserOut:
    return UserOut.model_validate(users.update(db, user_id, body))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DbDep, admin: AdminUser) -> None:
    users.delete(db, admin, user_id)
