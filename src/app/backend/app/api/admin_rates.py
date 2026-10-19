from fastapi import APIRouter, Depends

from app.db import DbDep
from app.schemas import ModelRateIn, ModelRateOut
from app.security import require_admin
from app.services import usage

router = APIRouter(
    prefix="/admin/model-rates", tags=["admin"], dependencies=[Depends(require_admin)]
)


@router.get("")
def list_rates(db: DbDep) -> list[ModelRateOut]:
    return [ModelRateOut.model_validate(rate) for rate in usage.list_rates(db)]


@router.put("/{model}")
def set_rate(model: str, body: ModelRateIn, db: DbDep) -> ModelRateOut:
    return ModelRateOut.model_validate(usage.set_rate(db, model, body))
