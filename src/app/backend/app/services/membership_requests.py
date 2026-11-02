"""Membership requests: public submissions, approved or rejected by an admin."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ConflictError, ErrorCode, NotFoundError
from app.models import MembershipRequest, MembershipRequestStatus, User
from app.schemas import MembershipRequestCreate, UserCreate
from app.services import users

Status = MembershipRequestStatus


def submit(db: Session, data: MembershipRequestCreate) -> None:
    """Record a request.

    Silent when the email already has an account or a pending request, so the public form
    can't be used to find out who is registered (or to flood the list).
    """
    if users.get_by_username(db, data.email) is not None:
        return
    pending = db.scalar(
        select(MembershipRequest).where(
            MembershipRequest.email == data.email, MembershipRequest.status == Status.PENDING
        )
    )
    if pending is None:
        db.add(MembershipRequest(email=data.email, details=data.details))
        db.flush()


def list_all(db: Session, status: Status | None = None) -> list[MembershipRequest]:
    query = select(MembershipRequest).order_by(MembershipRequest.created_at.desc())
    if status is not None:
        query = query.where(MembershipRequest.status == status)
    return list(db.scalars(query))


def _get_pending(db: Session, request_id: int) -> MembershipRequest:
    request = db.get(MembershipRequest, request_id)
    if request is None:
        msg = "Membership request not found"
        raise NotFoundError(ErrorCode.MEMBERSHIP_REQUEST_NOT_FOUND, msg)
    if request.status != Status.PENDING:
        msg = "Membership request was already decided"
        raise ConflictError(ErrorCode.MEMBERSHIP_REQUEST_DECIDED, msg)
    return request


def approve(db: Session, request_id: int, password: str) -> User:
    """Create the user (email as username, the app's default quota) and close the request."""
    request = _get_pending(db, request_id)
    user = users.create(db, UserCreate(username=request.email, password=password))
    request.status = Status.APPROVED
    request.decided_at = datetime.now(UTC)
    db.flush()
    return user


def reject(db: Session, request_id: int) -> MembershipRequest:
    request = _get_pending(db, request_id)
    request.status = Status.REJECTED
    request.decided_at = datetime.now(UTC)
    db.flush()
    return request
