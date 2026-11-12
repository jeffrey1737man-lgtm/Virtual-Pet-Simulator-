"""Application factory: wires Repository, Controller, Timer and the web routes."""
import os

from flask import Flask

from app.controllers.pet_controller import PetController
from app.repository.pet_repository import PetRepository
from app.routes import api
from app.services.timer_service import TimerService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app(config: dict | None = None, start_timer: bool = True) -> Flask:
    app = Flask(__name__)
    app.config["DATA_FILE"] = os.environ.get(
        "PET_DATA_FILE", os.path.join(BASE_DIR, "data", "pets.json")
    )
    app.config["TICK_SECONDS"] = float(os.environ.get("PET_TICK_SECONDS", 10))
    if config:
        app.config.update(config)

    repository = PetRepository(app.config["DATA_FILE"])
    controller = PetController(repository)
    controller.load_last_pet()  # FR-01: load the pet used last time, if any

    app.extensions["pet_controller"] = controller
    app.register_blueprint(api)

    if start_timer:
        timer = TimerService(controller.tick, app.config["TICK_SECONDS"])
        timer.start()
        app.extensions["timer_service"] = timer

    return app
