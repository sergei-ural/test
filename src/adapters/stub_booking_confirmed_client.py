import logging
import random

from domain.entities.booking import Booking
from domain.ports.booking_confirmed_client import BookingConfirmClient, ConfirmError

logger = logging.getLogger(__name__)


class StubBookingConfirmClient(BookingConfirmClient):
    async def confirm(self, booking: Booking) -> None:
        if random.random() < 0.15:
            raise ConfirmError()
        logger.info(
            "mock notification sent",
            extra={
                "booking_id": booking.id,
                "customer_name": booking.name,
                "service_type": booking.service_type,
                "booking_status": booking.status,
            },
        )
