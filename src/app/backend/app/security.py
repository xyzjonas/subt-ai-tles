from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.db import DbDep
from app.errors import ErrorCode, ForbiddenError, UnauthorizedError
from app.models import User
from app.services import users

_basic = HTTPBasic(auto_error=False)


def authenticated_user(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(_basic)], db: DbDep
) -> User:
    user = (
        users.authenticate(db, credentials.username, credentials.password)
        if credentials
        else None
    )
    if user is None:
        # No WWW-Authenticate challenge: it would make browsers show their native
        # login dialog instead of letting the frontend redirect to its login page.
        raise UnauthorizedError(ErrorCode.INVALID_CREDENTIALS, "Invalid credentials")
    return user


AuthenticatedUser = Annotated[User, Depends(authenticated_user)]


def current_user(user: AuthenticatedUser) -> User:
    if user.must_change_password:
        raise ForbiddenError(ErrorCode.PASSWORD_CHANGE_REQUIRED, "Password change required")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_admin(user: CurrentUser) -> User:
    if not user.is_admin:
        raise ForbiddenError(ErrorCode.ADMIN_ONLY, "Admin only")
    return user


AdminUser = Annotated[User, Depends(require_admin)]
