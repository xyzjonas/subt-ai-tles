from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.errors import ConflictError, ErrorCode, NotFoundError
from app.models import Folder, User


def list_for_user(db: Session, user: User) -> list[Folder]:
    query = select(Folder).where(Folder.owner_id == user.id).order_by(Folder.name)
    return list(db.scalars(query))


def get(db: Session, user: User, folder_id: str) -> Folder:
    folder = db.scalar(
        select(Folder).where(Folder.id == folder_id, Folder.owner_id == user.id)
    )
    if folder is None:
        msg = "Folder not found"
        raise NotFoundError(ErrorCode.FOLDER_NOT_FOUND, msg)
    return folder


def _clean(name: str) -> str:
    return " ".join(name.split())


def _named(db: Session, owner_id: int, name: str) -> Folder | None:
    """The owner's folder with this name, ignoring case."""
    return db.scalar(
        select(Folder).where(
            Folder.owner_id == owner_id, func.lower(Folder.name) == name.lower()
        )
    )


def create(db: Session, user: User, name: str) -> Folder:
    name = _clean(name)
    if _named(db, user.id, name) is not None:
        msg = "A folder with this name already exists"
        raise ConflictError(ErrorCode.FOLDER_NAME_TAKEN, msg, name=name)
    folder = Folder(owner_id=user.id, name=name)
    db.add(folder)
    db.flush()
    return folder


def rename(db: Session, user: User, folder_id: str, name: str) -> Folder:
    folder = get(db, user, folder_id)
    name = _clean(name)
    taken = _named(db, user.id, name)
    if taken is not None and taken.id != folder.id:
        msg = "A folder with this name already exists"
        raise ConflictError(ErrorCode.FOLDER_NAME_TAKEN, msg, name=name)
    folder.name = name
    db.flush()
    return folder


def delete(db: Session, user: User, folder_id: str) -> None:
    """Ungroups the folder's requests, they are kept."""
    db.delete(get(db, user, folder_id))
    db.flush()


def for_show(db: Session, owner_id: int, title: str) -> Folder:
    """The owner's folder named after a recognized show, created on first sight."""
    title = _clean(title)
    folder = _named(db, owner_id, title)
    if folder is None:
        folder = Folder(owner_id=owner_id, name=title[:100])
        db.add(folder)
        db.flush()
    return folder
