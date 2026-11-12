"""REST API + the single HTML page."""
from flask import Blueprint, current_app, jsonify, render_template, request

from app.controllers.pet_controller import NoActivePetError, PetNotFoundError

api = Blueprint("api", __name__)


def ctrl():
    return current_app.extensions["pet_controller"]


@api.get("/")
def index():
    return render_template("index.html")


@api.get("/api/pets")
def list_pets():
    return jsonify(ctrl().list_pets())


@api.post("/api/pets")
def create_pet():
    body = request.get_json(silent=True) or {}
    return jsonify(ctrl().create_pet(body.get("name", ""))), 201


@api.post("/api/pets/select")
def select_pet():
    body = request.get_json(silent=True) or {}
    return jsonify(ctrl().select_pet(body.get("name", "")))


@api.get("/api/pet")
def get_pet():
    return jsonify(ctrl().get_status())


@api.post("/api/pet/feed")
def feed():
    return jsonify(ctrl().feed_pet())


@api.post("/api/pet/play")
def play():
    return jsonify(ctrl().play_with_pet())


@api.post("/api/pet/save")
def save():
    return jsonify(ctrl().save_pet())


@api.errorhandler(ValueError)
def bad_request(err):
    return jsonify(error=str(err)), 400


@api.errorhandler(NoActivePetError)
def no_pet(err):
    return jsonify(error=str(err)), 404


@api.errorhandler(PetNotFoundError)
def not_found(err):
    return jsonify(error=str(err)), 404
