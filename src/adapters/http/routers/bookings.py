from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from fastapi.responses import JSONResponse

from adapters.http.factories import get_booking_repository, get_booking_service, get_create_booking_use_case
from adapters.http.rate_limit import enforce_create_booking_rate_limit
from adapters.http.schemas import BookingResponse, CreateBookingRequest, CreateBookingResponse
from domain.application_services.booking import BookingServiceApp
from domain.entities.booking import BookingStatus
from domain.ports.booking_repository import BookingNotFound, BookingNotPending, BookingRepository
from domain.use_cases.create_booking import CreateBookingUseCase

booking_router = APIRouter()


@booking_router.post("/bookings")
async def create_booking(
    body: CreateBookingRequest,
    create_booking_use_case: CreateBookingUseCase = Depends(get_create_booking_use_case),
    _: None = Depends(enforce_create_booking_rate_limit),
) -> Response:
    result = await create_booking_use_case.execute(
        datetime_=body.datetime,
        name=body.name,
        service_type=body.service_type,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED if result.created else status.HTTP_200_OK,
        content=CreateBookingResponse(id=result.id).model_dump(mode="json"),
    )


@booking_router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    booking_repository: BookingRepository = Depends(get_booking_repository),
) -> BookingResponse:
    try:
        booking = await booking_repository.get_by(id=booking_id)
    except BookingNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="booking not found") from exc
    return BookingResponse.from_booking(booking)


# TODO: Тут наверное нужно сделать пагинацию со стороны клиентского кода
@booking_router.get("/bookings", response_model=list[BookingResponse])
async def list_bookings(
    status: BookingStatus | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    booking_repository: BookingRepository = Depends(get_booking_repository),
) -> list[BookingResponse]:
    bookings = await booking_repository.find_by(status=status, offset=offset, limit=limit)
    return [BookingResponse.from_booking(booking) for booking in bookings]


@booking_router.delete("/bookings/{booking_id}")
async def cancel_booking(
    booking_id: int,
    booking_service: BookingServiceApp = Depends(get_booking_service),
) -> Response:
    try:
        await booking_service.cancel(booking_id)
    except BookingNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="booking not found") from exc
    except BookingNotPending as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="only pending bookings can be cancelled",
        ) from exc
    return Response(status_code=status.HTTP_200_OK)
