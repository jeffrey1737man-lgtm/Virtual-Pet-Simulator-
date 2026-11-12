"""PetController: the single entry point used by the web layer and the timer."""
import threading

from app.models.pet import Pet
from app.observers.autosave_observer import AutoSaveObserver
from app.observers.status_display import StatusDisplay
from app.repository.pet_repository import PetRepository

MAX_NAME_LENGTH = 24


class NoActivePetError(Exception):
    pass


class PetNotFoundError(Exception):
    pass


class PetController:
    def __init__(self, repository: PetRepository):
        self._repository = repository
        self._autosave = AutoSaveObserver(repository)
        self._pet: Pet | None = None
        self._display: StatusDisplay | None = None
        self._lock = threading.RLock()  # timer thread + web requests share the pet

    # ---- pet lifecycle (FR-01) ----------------------------------------
    def _activate(self, pet: Pet) -> None:
        self._pet = pet
        self._display = StatusDisplay(pet)
        pet.attach(self._display)
        pet.attach(self._autosave)

    def load_last_pet(self) -> bool:
        with self._lock:
            pet = self._repository.load()
            if pet:
                self._activate(pet)
            return pet is not None

    def create_pet(self, name: str) -> dict:
        name = (name or "").strip()
        if not name:
            raise ValueError("Give your pet a name.")
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError(f"Names can be at most {MAX_NAME_LENGTH} characters.")
        with self._lock:
            if self._repository.exists(name):
                raise ValueError(f"A pet named {name} already exists.")
            pet = Pet(name)
            self._activate(pet)
            self._repository.save(pet)
            return self.get_status()

    def select_pet(self, name: str) -> dict:
        with self._lock:
            pet = self._repository.load(name)
            if pet is None:
                raise PetNotFoundError(f"No pet named {name}.")
            self._activate(pet)
            self._repository.save(pet)  # remember it as the active pet
            return self.get_status()

    def list_pets(self) -> dict:
        with self._lock:
            return {
                "pets": self._repository.list_names(),
                "active": self._pet.name if self._pet else None,
            }

    # ---- actions (FR-03, FR-04, FR-05) --------------------------------
    def _require_pet(self) -> Pet:
        if self._pet is None:
            raise NoActivePetError("Create or select a pet first.")
        return self._pet

    def feed_pet(self) -> dict:
        with self._lock:
            self._require_pet().feed()
            return self.get_status()

    def play_with_pet(self) -> dict:
        with self._lock:
            self._require_pet().play()
            return self.get_status()

    def tick(self) -> None:
        """Called by the TimerService."""
        with self._lock:
            if self._pet is not None:
                self._pet.update_status()

    # ---- queries / persistence (FR-02, FR-08) -------------------------
    def get_status(self) -> dict:
        with self._lock:
            pet = self._require_pet()
            data = pet.to_dict()
            data["summary"] = self._display.display_status()
            return data

    def save_pet(self) -> dict:
        with self._lock:
            self._repository.save(self._require_pet())
            return self.get_status()
