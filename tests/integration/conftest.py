import pytest

from adapters.settings import settings


@pytest.fixture(autouse=True)
def celery_eager() -> None:
    from adapters.celery_app import celery_app
    from adapters.tasks.confirm_booking import confirm_booking_task

    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        broker_url=settings.celery_broker_url,
        result_backend=settings.celery_result_backend,
    )
    confirm_booking_task.max_retries = 2
    confirm_booking_task.default_retry_delay = 10
    yield
