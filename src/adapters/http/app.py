from fastapi import FastAPI

from adapters.http.routers.bookings import booking_router
from adapters.logging_config import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI()
    app.include_router(booking_router)
    return app


app = create_app()
