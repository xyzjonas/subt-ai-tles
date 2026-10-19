import asyncio

from celery import Celery  # type: ignore[import-untyped]

from app.config import settings
from app.services import translation

celery_app = Celery("subtaitles", broker=settings.redis_url)
celery_app.conf.update(
    # A job interrupted by a worker restart is redelivered; `run_job` is idempotent and the
    # translation cache makes the retry cheap.
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    # Redis redelivers unacknowledged tasks after this; it must exceed the longest job.
    broker_transport_options={"visibility_timeout": 6 * 60 * 60},
)


@celery_app.task(name="translate_job")
def translate_job(job_id: str) -> None:
    asyncio.run(translation.run_job(job_id))
