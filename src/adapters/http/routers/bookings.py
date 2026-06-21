from fastapi import APIRouter, Depends, Response, status

from adapters.http.dependencies import get_booking_service
from adapters.http.schemas import CreateBookingRequest
from domain.application_services.booking import BookingServiceApplication
from domain.ports.booking_repository import BookingAlreadyExist

booking_router = APIRouter()


@booking_router.post("/bookings")
async def create_booking(
    body: CreateBookingRequest,
    booking_service: BookingServiceApplication = Depends(get_booking_service),
) -> Response:
    try:
        await booking_service.create(datetime_=body.datetime, name=body.name, service_type=body.service_type)
    except BookingAlreadyExist:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_201_CREATED)
