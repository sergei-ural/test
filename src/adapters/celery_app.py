from celery import Celery

from adapters.settings import settings

celery_app = Celery("booking_app")
celery_app.conf.update(
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend,
)

import adapters.tasks.confirm_booking  # noqa: E402, F401
