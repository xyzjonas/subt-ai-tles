import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.errors import ConflictError, NotFoundError
from app.models import User
from app.passwords import DUMMY_HASH, hash_password, verify_password
from app.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


def list_all(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.username)))


def get(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        msg = "User not found"
        raise NotFoundError(msg)
    return user


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def _active_admin_count(db: Session) -> int:
    return db.scalar(
        select(func.count()).select_from(User).where(User.is_admin, User.is_active)
    ) or 0


def _is_active_admin(user: User) -> bool:
    return user.is_admin and user.is_active


def create(db: Session, data: UserCreate) -> User:
    if get_by_username(db, data.username) is not None:
        msg = "Username already taken"
        raise ConflictError(msg)
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        is_admin=data.is_admin,
    )
    db.add(user)
    db.flush()
    return user


def update(db: Session, user_id: int, data: UserUpdate) -> User:
    user = get(db, user_id)
    was_active_admin = _is_active_admin(user)
    if data.password is not None:
        user.password_hash = hash_password(data.password)
    if data.is_admin is not None:
        user.is_admin = data.is_admin
    if data.is_active is not None:
        user.is_active = data.is_active
    if was_active_admin and not _is_active_admin(user) and _active_admin_count(db) <= 1:
        db.rollback()
        msg = "Cannot demote or deactivate the last admin"
        raise ConflictError(msg)
    db.flush()
    return user


def delete(db: Session, acting: User, user_id: int) -> None:
    user = get(db, user_id)
    if user.id == acting.id:
        msg = "Cannot delete yourself"
        raise ConflictError(msg)
    if _is_active_admin(user) and _active_admin_count(db) <= 1:
        msg = "Cannot delete the last admin"
        raise ConflictError(msg)
    db.delete(user)
    db.flush()


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = get_by_username(db, username)
    if user is None:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.password_hash) or not user.is_active:
        return None
    return user


def ensure_bootstrap_admin(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(User)):
        return
    if not (settings.admin_username and settings.admin_password):
        logger.warning(
            "No users exist; set ADMIN_USERNAME and ADMIN_PASSWORD to bootstrap an admin"
        )
        return
    create(
        db,
        UserCreate(
            username=settings.admin_username, password=settings.admin_password, is_admin=True
        ),
    )
    db.commit()
