from celery import Celery

from adapters.logging_config import configure_logging
from adapters.settings import settings
# TODO:Вызывается в двух местах, точно ли так нормально?
configure_logging()

celery_app = Celery("booking_app")
celery_app.conf.update(
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend,
)

import adapters.tasks.confirm_booking  # noqa: E402, F401
