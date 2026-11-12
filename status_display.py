"""Concrete Observer: keeps the latest status that the UI shows."""
import logging

from app.observers.pet_observer import PetObserver

log = logging.getLogger(__name__)


class StatusDisplay(PetObserver):
    def __init__(self, pet=None):
        self._pet = pet
        self._snapshot: dict | None = None
        if pet is not None:
            self._snapshot = pet.to_dict()

    def update(self, pet) -> None:
        """FR-07: refresh the display after the pet notifies us."""
        self._pet = pet
        self._snapshot = pet.to_dict()
        log.info(self.display_status())

    def display_status(self) -> str:
        if self._snapshot is None:
            return "No pet to display."
        s = self._snapshot
        return (
            f"{s['name']} is {s['status']} "
            f"(hunger {s['hunger']}/100, happiness {s['happiness']}/100)"
        )

    @property
    def snapshot(self) -> dict | None:
        return self._snapshot
