"""System Timer actor: calls a callback every N seconds (FR-05)."""
import threading


class TimerService:
    def __init__(self, callback, interval_seconds: float):
        self._callback = callback
        self._interval = interval_seconds
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True, name="pet-timer")

    def start(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        while not self._stop.wait(self._interval):
            self._callback()
