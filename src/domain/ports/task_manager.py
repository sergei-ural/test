from abc import ABC, abstractmethod


class TaskManager(ABC):
    @abstractmethod
    def confirm(self, booking_id: int) -> None:
        ...
