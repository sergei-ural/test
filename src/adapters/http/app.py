from fastapi import FastAPI

from adapters.http.routers.bookings import booking_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(booking_router)
    return app


app = create_app()
