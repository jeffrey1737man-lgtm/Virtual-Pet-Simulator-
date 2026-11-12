"""PetRepository: saves/loads pets in a JSON file (FR-08).

Writes are atomic (temp file + replace) so a crash can't corrupt the file,
and a damaged file is set aside instead of crashing the app.
"""
import json
import os
import shutil
import threading

from app.models.pet import Pet


class PetRepository:
    def __init__(self, path: str):
        self._path = path
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)

    def _read(self) -> dict:
        if not os.path.exists(self._path):
            return {"active": None, "pets": {}}
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict) or not isinstance(data.get("pets"), dict):
                raise ValueError("unexpected structure")
            data.setdefault("active", None)
            return data
        except (json.JSONDecodeError, ValueError, OSError):
            shutil.move(self._path, self._path + ".corrupt")
            return {"active": None, "pets": {}}

    def _write(self, data: dict) -> None:
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp, self._path)

    def save(self, pet: Pet) -> None:
        with self._lock:
            data = self._read()
            data["pets"][pet.name] = pet.to_dict()
            data["active"] = pet.name
            self._write(data)

    def load(self, name: str | None = None) -> Pet | None:
        """Load a pet by name, or the most recently used one if name is None."""
        with self._lock:
            data = self._read()
            key = name or data.get("active")
            record = data["pets"].get(key) if key else None
            return Pet.from_dict(record) if record else None

    def list_names(self) -> list[str]:
        with self._lock:
            return sorted(self._read()["pets"].keys(), key=str.lower)

    def exists(self, name: str) -> bool:
        return name.lower() in (n.lower() for n in self.list_names())
