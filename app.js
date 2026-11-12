/* Front end for the Virtual Pet Simulator.
 *
 * The Observer pattern is used here too:
 *   PetStore  = Subject   (holds the latest pet state)
 *   render*   = Observers (each view subscribes and redraws on change)
 */

class PetStore {
  constructor() { this.state = null; this.observers = []; }
  subscribe(fn) { this.observers.push(fn); }
  set(state) { this.state = state; this.observers.forEach((fn) => fn(state)); }
}

const store = new PetStore();
const $ = (id) => document.getElementById(id);

async function api(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

let toastTimer;
function toast(message, isError = false) {
  const el = $("toast");
  el.textContent = message;
  el.className = "toast show" + (isError ? " error" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (el.className = "toast"), 2200);
}

/* ---------- face drawing ---------- */
const MOUTHS = {
  Happy:    { d: "M74 134 Q100 160 126 134", open: false },
  Normal:   { d: "M82 138 Q100 148 118 138", open: false },
  Unhappy:  { d: "M78 148 Q100 128 122 148", open: false },
  Hungry:   { d: "M88 134 Q100 158 112 134 Z", open: true },
  Critical: { d: "M80 150 Q100 132 120 150", open: false },
};

function eyes(status) {
  if (status === "Critical") {
    const x = (cx) =>
      `<path d="M${cx - 8} 92 L${cx + 8} 108 M${cx + 8} 92 L${cx - 8} 108" stroke="#1d2340" stroke-width="5" stroke-linecap="round"/>`;
    return x(76) + x(124);
  }
  if (status === "Happy") {
    const arc = (cx) =>
      `<path d="M${cx - 9} 104 Q${cx} 90 ${cx + 9} 104" fill="none" stroke="#1d2340" stroke-width="5" stroke-linecap="round"/>`;
    return arc(76) + arc(124);
  }
  const ry = status === "Unhappy" ? 7 : 10;
  const eye = (cx) =>
    `<ellipse cx="${cx}" cy="100" rx="9" ry="${ry}" fill="#1d2340"/><circle cx="${cx + 3}" cy="96" r="3" fill="#fff"/>`;
  return eye(76) + eye(124);
}

/* ---------- observers (views) ---------- */
function renderPet(pet) {
  const has = !!pet;
  $("stage").hidden = !has;
  $("welcome").hidden = has;
  if (!has) return;

  const status = pet.status;
  $("pet-wrap").className = "pet " + status.toLowerCase();
  $("eyes").innerHTML = eyes(status);
  const mouth = MOUTHS[status] || MOUTHS.Normal;
  $("mouth").setAttribute("d", mouth.d);
  $("mouth").setAttribute("class", mouth.open ? "open" : "");

  $("pet-name").textContent = pet.name;
  const pill = $("pet-condition");
  pill.textContent = status;
  pill.className = "pill " + status;
  $("pet-event").textContent = pet.last_event;

  $("hunger-val").textContent = pet.hunger;
  $("hunger-bar").style.width = pet.hunger + "%";
  $("happiness-val").textContent = pet.happiness;
  $("happiness-bar").style.width = pet.happiness + "%";
}
store.subscribe(renderPet);

async function refreshPetList() {
  const { pets, active } = await api("GET", "/api/pets");
  const select = $("pet-select");
  select.innerHTML = "";
  pets.forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    opt.selected = name === active;
    select.appendChild(opt);
  });
  select.hidden = pets.length === 0;
}

/* ---------- user actions ---------- */
async function act(path, message) {
  try {
    store.set(await api("POST", path));
    if (message) toast(message);
  } catch (err) {
    toast(err.message, true);
  }
}

$("btn-feed").addEventListener("click", () => act("/api/pet/feed"));
$("btn-play").addEventListener("click", () => act("/api/pet/play"));
$("btn-save").addEventListener("click", () => act("/api/pet/save", "Saved"));

$("new-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    store.set(await api("POST", "/api/pets", { name: $("new-name").value }));
    $("new-name").value = "";
    await refreshPetList();
    toast("Welcome home!");
  } catch (err) {
    toast(err.message, true);
  }
});

$("pet-select").addEventListener("change", async (e) => {
  try {
    store.set(await api("POST", "/api/pets/select", { name: e.target.value }));
  } catch (err) {
    toast(err.message, true);
  }
});

/* ---------- polling: the server timer changes the pet, so we re-read it ---------- */
async function poll() {
  try {
    store.set(await api("GET", "/api/pet"));
  } catch (_) {
    if (store.state !== null) store.set(null);
  }
}

(async function init() {
  await refreshPetList();
  await poll();
  setInterval(poll, 2000);
})();
