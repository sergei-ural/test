from copy import deepcopy
from datetime import datetime

from domain.entities.booking import Booking, BookingStatus


def make_from[Entity](obj: Entity, **kwargs) -> Entity:
    new_obj = deepcopy(obj)
    for key, value in kwargs.items():
        if not hasattr(obj, key):
            raise AttributeError(f"Object {obj.__class__.__name__} has no attribute {key}")
        setattr(new_obj, key, deepcopy(value))
    return new_obj


def make_booking(
    *,
    id: int | None = None,
    name: str = "name",
    service_type: str = "service_type",
    status: BookingStatus = BookingStatus.PENDING,
    datetime_: datetime | None = None,
) -> Booking:
    return Booking(
        id=id,
        datetime=datetime_ or datetime(2026, 6, 21, 10, 0),
        name=name,
        service_type=service_type,
        status=status,
    )
