from fastapi import APIRouter, Depends, status

from app.db import DbDep
from app.models import MembershipRequestStatus
from app.schemas import (
    MembershipRequestApprove,
    MembershipRequestCreate,
    MembershipRequestOut,
    UserOut,
)
from app.security import require_admin
from app.services import membership_requests

router = APIRouter(tags=["membership"])


@router.post("/membership-requests", status_code=status.HTTP_202_ACCEPTED)
def submit_request(body: MembershipRequestCreate, db: DbDep) -> None:
    """Public: no sign-in. The answer is the same whether or not anything was stored."""
    membership_requests.submit(db, body)


admin = APIRouter(
    prefix="/admin/membership-requests", dependencies=[Depends(require_admin)], tags=["admin"]
)


@admin.get("")
def list_requests(
    db: DbDep, status: MembershipRequestStatus | None = None
) -> list[MembershipRequestOut]:
    rows = membership_requests.list_all(db, status)
    return [MembershipRequestOut.model_validate(r) for r in rows]


@admin.post("/{request_id}/approve", status_code=status.HTTP_201_CREATED)
def approve_request(request_id: int, body: MembershipRequestApprove, db: DbDep) -> UserOut:
    return UserOut.model_validate(membership_requests.approve(db, request_id, body.password))


@admin.post("/{request_id}/reject")
def reject_request(request_id: int, db: DbDep) -> MembershipRequestOut:
    return MembershipRequestOut.model_validate(membership_requests.reject(db, request_id))


router.include_router(admin)
