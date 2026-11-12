import os
import tempfile
import unittest

from app.controllers.pet_controller import NoActivePetError, PetController
from app.models.pet import CRITICAL, HAPPY, HUNGRY, Pet
from app.observers.pet_observer import PetObserver
from app.repository.pet_repository import PetRepository


class Spy(PetObserver):
    def __init__(self):
        self.calls = 0

    def update(self, pet):
        self.calls += 1


class PetTests(unittest.TestCase):
    def test_values_stay_in_range(self):
        pet = Pet("A", hunger=0, happiness=100)
        pet.feed()
        pet.play()
        self.assertTrue(0 <= pet.hunger <= 100)
        self.assertTrue(0 <= pet.happiness <= 100)
        for _ in range(100):
            pet.update_status()
        self.assertEqual(pet.hunger, 100)
        self.assertEqual(pet.happiness, 0)

    def test_observers_are_notified_on_every_change(self):
        pet, spy = Pet("A"), Spy()
        pet.attach(spy)
        pet.feed()
        pet.play()
        pet.update_status()
        self.assertEqual(spy.calls, 3)
        pet.detach(spy)
        pet.feed()
        self.assertEqual(spy.calls, 3)

    def test_conditions(self):
        self.assertEqual(Pet("A", hunger=10, happiness=90).status, HAPPY)
        self.assertEqual(Pet("A", hunger=70, happiness=60).status, HUNGRY)
        self.assertEqual(Pet("A", hunger=95, happiness=60).status, CRITICAL)


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.repo = PetRepository(os.path.join(self.dir.name, "pets.json"))

    def tearDown(self):
        self.dir.cleanup()

    def test_save_and_load(self):
        pet = Pet("Mochi", hunger=40, happiness=55)
        self.repo.save(pet)
        loaded = self.repo.load()
        self.assertEqual((loaded.name, loaded.hunger, loaded.happiness), ("Mochi", 40, 55))

    def test_controller_autosaves_and_requires_pet(self):
        ctrl = PetController(self.repo)
        with self.assertRaises(NoActivePetError):
            ctrl.feed_pet()
        ctrl.create_pet("Pixel")
        ctrl.play_with_pet()
        self.assertEqual(self.repo.load("Pixel").happiness, 90)


if __name__ == "__main__":
    unittest.main()
