from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.db import DbDep
from app.models import User
from app.services import users

_basic = HTTPBasic(auto_error=False)


def current_user(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(_basic)], db: DbDep
) -> User:
    user = (
        users.authenticate(db, credentials.username, credentials.password)
        if credentials
        else None
    )
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": 'Basic realm="subt-ai-tles", charset="UTF-8"'},
        )
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_admin(user: CurrentUser) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user


AdminUser = Annotated[User, Depends(require_admin)]
