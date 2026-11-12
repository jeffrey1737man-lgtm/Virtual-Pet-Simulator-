"""Second Concrete Observer: saves the pet every time it changes.

Shows the Scalability requirement: new observers can be added without
touching the Pet class.
"""
import logging

from app.observers.pet_observer import PetObserver

log = logging.getLogger(__name__)


class AutoSaveObserver(PetObserver):
    def __init__(self, repository):
        self._repository = repository

    def update(self, pet) -> None:
        try:
            self._repository.save(pet)
        except OSError as exc:  # never let a disk problem break the pet
            log.error("Auto-save failed: %s", exc)
