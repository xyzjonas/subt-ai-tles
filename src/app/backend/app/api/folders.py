from fastapi import APIRouter, status

from app.db import DbDep
from app.schemas import FolderIn, FolderOut
from app.security import CurrentUser
from app.services import folders

router = APIRouter(prefix="/folders", tags=["folders"])


@router.get("")
def list_folders(db: DbDep, user: CurrentUser) -> list[FolderOut]:
    return [FolderOut.model_validate(f) for f in folders.list_for_user(db, user)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_folder(body: FolderIn, db: DbDep, user: CurrentUser) -> FolderOut:
    return FolderOut.model_validate(folders.create(db, user, body.name))


@router.patch("/{folder_id}")
def rename_folder(folder_id: str, body: FolderIn, db: DbDep, user: CurrentUser) -> FolderOut:
    return FolderOut.model_validate(folders.rename(db, user, folder_id, body.name))


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(folder_id: str, db: DbDep, user: CurrentUser) -> None:
    folders.delete(db, user, folder_id)
