Virtual Pet Simulator
Care for a virtual pet. Hunger and happiness change through your actions and a background timer, and every display refreshes automatically using the Observer pattern. Built from the SRS + six UML diagrams of the OOSE project.
Stack: Python 3 + Flask (backend, REST API) · HTML / CSS / JavaScript (front end) · JSON file (persistence)
Run it
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
Open http://127.0.0.1:5000
Optional settings (environment variables): PET_TICK_SECONDS (default 10), PORT (default 5000), PET_DATA_FILE.
Run the tests
python -m unittest discover -s tests -v
Project structure
virtual-pet-simulator/
├── run.py                              # starts the app
├── requirements.txt
├── app/
│   ├── __init__.py                     # app factory (wires everything)
│   ├── routes.py                       # REST API + page
│   ├── models/pet.py                   # Pet = Subject
│   ├── observers/
│   │   ├── pet_observer.py             # PetObserver interface
│   │   ├── status_display.py           # StatusDisplay (concrete observer)
│   │   └── autosave_observer.py        # AutoSaveObserver (concrete observer)
│   ├── controllers/pet_controller.py   # PetController
│   ├── repository/pet_repository.py    # PetRepository (JSON file)
│   ├── services/timer_service.py       # System Timer
│   ├── templates/index.html            # User Interface
│   └── static/{css/style.css, js/app.js}
├── data/                               # saved pets (pets.json, git-ignored)
└── tests/test_pet.py
SRS requirements → code
ID
Where
FR-01 Create / load pet
PetController.create_pet / select_pet / load_last_pet
FR-02 Show hunger, happiness, condition
GET /api/pet, static/js/app.js
FR-03 Feed
Pet.feed, POST /api/pet/feed
FR-04 Play
Pet.play, POST /api/pet/play
FR-05 Timer updates
TimerService → PetController.tick → Pet.update_status
FR-06 Notify observers
Pet.notify_observers
FR-07 Refresh display
StatusDisplay.update, front-end PetStore
FR-08 Save / load
PetRepository, AutoSaveObserver, POST /api/pet/save
FR-09 Valid range
clamp() in models/pet.py
FR-10 Condition
Pet.derive_status (Happy, Normal, Hungry, Unhappy, Critical)
API
Method
Path
Purpose
GET
/api/pets
list pets and the active one
POST
/api/pets
create a pet {"name": "Mochi"}
POST
/api/pets/select
switch pet {"name": "Mochi"}
GET
/api/pet
current status
POST
/api/pet/feed
feed
POST
/api/pet/play
play
POST
/api/pet/save
save now