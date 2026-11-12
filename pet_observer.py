"""Observer interface of the Observer pattern."""
from abc import ABC, abstractmethod


class PetObserver(ABC):
    """Anything that wants to be told when a Pet changes implements this."""

    @abstractmethod
    def update(self, pet) -> None:
        """Called by the Pet (Subject) after its state changes."""
