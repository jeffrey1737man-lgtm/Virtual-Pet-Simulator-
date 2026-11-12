"""Pet = Subject of the Observer pattern.

hunger:     0 (full) ... 100 (starving)   -> higher is worse
happiness:  0 (sad)  ... 100 (joyful)     -> higher is better
"""
from __future__ import annotations

MIN_VALUE = 0
MAX_VALUE = 100

# Conditions (FR-10 and the state diagram)
HAPPY = "Happy"
NORMAL = "Normal"
HUNGRY = "Hungry"
UNHAPPY = "Unhappy"
CRITICAL = "Critical"


def clamp(value: int) -> int:
    """FR-09: keep values inside the valid range."""
    return max(MIN_VALUE, min(MAX_VALUE, int(value)))


class Pet:
    FEED_HUNGER_DROP = 25
    FEED_HAPPINESS_GAIN = 5
    PLAY_HAPPINESS_GAIN = 20
    PLAY_HUNGER_GAIN = 10
    TICK_HUNGER_GAIN = 5
    TICK_HAPPINESS_DROP = 4

    def __init__(self, name: str, hunger: int = 30, happiness: int = 70,
                 last_event: str = "Hello!"):
        self.name = name
        self._hunger = clamp(hunger)
        self._happiness = clamp(happiness)
        self.last_event = last_event
        self._observers: list = []
        self.status = self.derive_status()

    # ---- state ---------------------------------------------------------
    @property
    def hunger(self) -> int:
        return self._hunger

    @property
    def happiness(self) -> int:
        return self._happiness

    def derive_status(self) -> str:
        """FR-10: derive the overall condition from hunger + happiness."""
        if self._hunger >= 85 or self._happiness <= 15:
            return CRITICAL
        if self._hunger >= 65:
            return HUNGRY
        if self._happiness <= 35:
            return UNHAPPY
        if self._happiness >= 75 and self._hunger <= 35:
            return HAPPY
        return NORMAL

    # ---- actions (FR-03, FR-04, FR-05) ---------------------------------
    def feed(self) -> None:
        self._hunger = clamp(self._hunger - self.FEED_HUNGER_DROP)
        self._happiness = clamp(self._happiness + self.FEED_HAPPINESS_GAIN)
        self._changed(f"{self.name} enjoyed a meal.")

    def play(self) -> None:
        self._happiness = clamp(self._happiness + self.PLAY_HAPPINESS_GAIN)
        self._hunger = clamp(self._hunger + self.PLAY_HUNGER_GAIN)
        self._changed(f"{self.name} had fun playing.")

    def update_status(self) -> None:
        """Called by the timer: time passes, pet gets hungrier and a bit sadder."""
        self._hunger = clamp(self._hunger + self.TICK_HUNGER_GAIN)
        self._happiness = clamp(self._happiness - self.TICK_HAPPINESS_DROP)
        self._changed("Time passed.")

    # alias that matches the class diagram name
    updateStatus = update_status

    def _changed(self, event: str) -> None:
        self.status = self.derive_status()
        self.last_event = event
        self.notify_observers()  # FR-06

    # ---- Subject side of the Observer pattern --------------------------
    def attach(self, observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self) -> None:
        for observer in list(self._observers):
            observer.update(self)

    notifyObservers = notify_observers

    # ---- persistence helpers ------------------------------------------
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "hunger": self._hunger,
            "happiness": self._happiness,
            "status": self.status,
            "last_event": self.last_event,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        return cls(
            name=str(data["name"]),
            hunger=data.get("hunger", 30),
            happiness=data.get("happiness", 70),
            last_event=data.get("last_event", "Welcome back!"),
        )
