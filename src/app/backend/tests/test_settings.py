from collections.abc import Callable, Iterator

import pytest
from app.db import SessionLocal
from app.models import AppSettings, ModelRate
from app.services import app_settings, translation
from fastapi.testclient import TestClient

from tests.conftest import ADMIN, FakeQueue, StubTranslator
from tests.test_api import _finish, _upload
from tests.test_usage import _records

URL = "/api/admin/settings"


@pytest.fixture(autouse=True)
def restore_defaults() -> Iterator[None]:
    yield
    with SessionLocal() as db:
        row = app_settings.get(db)
        row.model, row.temperature = "gpt-4.1-nano", 0.0
        db.commit()


def test_defaults_and_catalog(client: TestClient) -> None:
    body = client.get(URL, auth=ADMIN).json()

    assert body["model"] == "gpt-4.1-nano"
    assert body["temperature"] == 0
    models = {m["id"]: m for m in body["models"]}
    assert set(models) == {"gpt-4.1-nano", "gpt-5-nano", "gpt-6-luna"}
    assert models["gpt-4.1-nano"]["supportsTemperature"] is True
    assert models["gpt-5-nano"]["supportsTemperature"] is False
    assert models["gpt-6-luna"]["inputCreditsPer1K"] == 1.0
    assert models["gpt-6-luna"]["outputCreditsPer1K"] == 5.0
    assert models["gpt-4.1-nano"]["description"]


def test_admin_only(client: TestClient, make_user: Callable) -> None:
    kim = make_user("kim")

    assert client.get(URL, auth=kim).status_code == 403
    r = client.put(URL, json={"model": "gpt-5-nano", "temperature": 0.5}, auth=kim)
    assert r.status_code == 403


def test_update(client: TestClient) -> None:
    r = client.put(URL, json={"model": "gpt-5-nano", "temperature": 0.4}, auth=ADMIN)

    assert r.status_code == 200
    assert (r.json()["model"], r.json()["temperature"]) == ("gpt-5-nano", 0.4)
    assert client.get(URL, auth=ADMIN).json()["model"] == "gpt-5-nano"


@pytest.mark.parametrize(
    "body",
    [
        {"model": "gpt-unknown", "temperature": 0},
        {"model": "gpt-5-nano", "temperature": 1.5},
        {"model": "gpt-5-nano", "temperature": -0.1},
        {"model": "gpt-5-nano"},
    ],
)
def test_invalid_update(client: TestClient, body: dict) -> None:
    assert client.put(URL, json=body, auth=ADMIN).status_code == 422


def test_model_without_rate_is_rejected(client: TestClient) -> None:
    with SessionLocal() as db:
        rate = db.get(ModelRate, "gpt-6-luna")
        saved = (rate.input_credits_per_1k, rate.output_credits_per_1k)
        db.delete(rate)
        db.commit()
    try:
        r = client.put(URL, json={"model": "gpt-6-luna", "temperature": 0}, auth=ADMIN)
    finally:
        with SessionLocal() as db:
            db.add(
                ModelRate(
                    model="gpt-6-luna",
                    input_credits_per_1k=saved[0],
                    output_credits_per_1k=saved[1],
                )
            )
            db.commit()

    assert r.status_code == 422


def test_effective_temperature() -> None:
    assert (
        app_settings.effective_temperature(AppSettings(model="gpt-4.1-nano", temperature=0.3))
        == 0.3
    )
    assert (
        app_settings.effective_temperature(AppSettings(model="gpt-5-nano", temperature=0.3))
        is None
    )


def test_make_translator_uses_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.undo()  # the autouse stub replaces make_translator
    monkeypatch.setattr(translation.settings, "openai_api_key", "key")

    warm = translation.make_translator(AppSettings(model="gpt-4.1-nano", temperature=0.4), {})
    reasoning = translation.make_translator(
        AppSettings(model="gpt-5-nano", temperature=0.4), {}
    )

    assert (warm.model, warm.temperature) == ("gpt-4.1-nano", 0.4)
    assert (reasoning.model, reasoning.temperature) == ("gpt-5-nano", None)


def test_job_uses_configured_model(
    client: TestClient,
    make_user: Callable,
    queue: FakeQueue,
    translator: StubTranslator,
) -> None:
    mia = make_user("mia")
    client.put(URL, json={"model": "gpt-6-luna", "temperature": 0.4}, auth=ADMIN)

    _finish(client, queue, mia, _upload(client, mia)["id"])

    (record,) = _records(client, mia)
    assert record["model"] == "gpt-6-luna"
    assert record["credits"] == 2000 * 1.0 / 1000 + 1000 * 5.0 / 1000
    assert translator.temperature is None  # gpt-6-luna takes no temperature
