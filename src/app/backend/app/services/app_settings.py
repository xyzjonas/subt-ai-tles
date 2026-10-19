"""Global, admin-editable settings: which model translates and how freely."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import InvalidInputError
from app.models import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    MODEL_INFO,
    AppSettings,
    ModelRate,
    TranslationModel,
)
from app.models.app_settings import SINGLETON_ID
from app.schemas import AppSettingsIn, AppSettingsOut, ModelOption


def get(db: Session) -> AppSettings:
    settings = db.get(AppSettings, SINGLETON_ID)
    if settings is None:  # the migration seeds it; this only covers a hand-emptied table
        settings = AppSettings(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE)
        db.add(settings)
        db.flush()
    return settings


def effective_temperature(settings: AppSettings) -> float | None:
    """Return the temperature to send, or None if the model takes none."""
    info = MODEL_INFO.get(TranslationModel(settings.model))
    return settings.temperature if info and info.supports_temperature else None


def update(db: Session, data: AppSettingsIn) -> AppSettings:
    if db.get(ModelRate, data.model) is None:
        msg = f"Model {data.model} has no credit rate yet"
        raise InvalidInputError(msg)
    settings = get(db)
    settings.model = data.model
    settings.temperature = data.temperature
    db.flush()
    return settings


def view(db: Session) -> AppSettingsOut:
    """Return the current settings plus the catalog (with credit rates) to choose from."""
    settings = get(db)
    rates = {rate.model: rate for rate in db.scalars(select(ModelRate))}
    options = [
        ModelOption(
            id=model,
            label=info.label,
            description=info.description,
            supports_temperature=info.supports_temperature,
            input_credits_per_1k=rates[model].input_credits_per_1k,
            output_credits_per_1k=rates[model].output_credits_per_1k,
        )
        for model, info in MODEL_INFO.items()
        if model in rates
    ]
    return AppSettingsOut(
        model=TranslationModel(settings.model),
        temperature=settings.temperature,
        models=options,
    )
