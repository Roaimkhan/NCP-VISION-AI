# NCP-VISION AI — MVP Implementation Plan (for Codex)

> **Read this whole file first. Then execute ONE phase at a time, in order.**
> Goal: a **demo-able** prototype in hours, not days. Everything is synthetic data. Anything not in this file is OUT OF SCOPE.

---

## Current status

- Final compressed demo flow is implemented and working.
- The app is kept in the reduced-scope mode described by the updated project deadline.
- Run instructions are now documented in README.md.

## 0. GOLDEN RULES (Codex: obey these, they override your instincts)

1. **Demo path first.** If a feature is not in the Demo Script (section 3), it is not built until all phases are done.
2. **One phase at a time.** Finish → run that phase's `VERIFY` commands → commit → next phase. Never start phase N+1 with phase N failing.
3. **No new libraries** beyond section 2. No new frameworks, no ORMs other than SQLModel, no state libs, no UI kits except Tailwind.
4. **No refactors, no renames, no "improvements."** Use the exact file paths, endpoint paths, enum values and field names below.
5. **Do not ask questions.** If something is ambiguous, pick the simplest option, and append one line to `DECISIONS.md`.
6. **Deterministic AI.** Duplicate/anomaly detection = plain Python rules + `rapidfuzz`. No LLM calls, no network calls at runtime.
7. **AI never decides legality.** It only creates *alerts*. Only a human officer action changes status. Never write words like "illegal", "approved for customs", "eligible". Use "Profile Verified".
8. **Everything is labelled synthetic.** A banner on every page: `DEMO — synthetic data. Profiling is not registration, customs clearance, or eligibility for any scheme.`
9. **If OCR fails, the form still works** (fields stay empty for manual entry). Never block the citizen flow on OCR.
10. Keep every file small. No file over ~300 lines.

---

## 1. WHAT WE ARE BUILDING (one paragraph)

Two web portals on one app. **Citizen Portal:** log in → upload a registration/import document → OCR pre-fills chassis/engine/make/year → citizen reviews and submits → gets tracking number `NCP-KP-2026-000123` → can track status and answer an officer's info request. **Government Dashboard:** officer logs in → sees stats, district chart, filterable list → opens an application → sees AI alerts (duplicates, anomalies, OCR mismatch) with side-by-side comparison → takes a human action (start review / request info / verify / close incomplete) → audit log records it → can export a district CSV report.

---

## 2. STACK (fixed — do not deviate)

| Layer | Choice | Note |
|---|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind + `recharts` | Proxy `/api/*` → `http://localhost:8000` via `next.config.js` rewrites (no CORS pain) |
| Backend | Python 3.11 + FastAPI + SQLModel + uvicorn + python-multipart | |
| DB | **SQLite** file `backend/ncp.db` | Postgres swap later is a one-line `DATABASE_URL` change. Do NOT set up Postgres now. |
| OCR | **EasyOCR** (CPU, `gpu=False`, languages `["en"]`) + OpenCV-headless + Pillow | Load reader ONCE at app startup |
| Matching | **rapidfuzz** (`fuzz.ratio`) | Replaces scikit-learn — not needed for MVP |
| Auth | JWT (`pyjwt`), 3 hardcoded demo roles | |
| Tests | pytest + httpx | |

`backend/requirements.txt`:
```
fastapi
uvicorn[standard]
sqlmodel
python-multipart
pyjwt
easyocr
opencv-python-headless
pillow
rapidfuzz
pytest
httpx
```

---

## 3. DEMO SCRIPT (the ONLY thing that must work flawlessly)

1. Open `/` → banner visible → click **Citizen Login** (`citizen1` / `demo123`).
2. `/citizen/apply` → upload `demo_assets/sample_docs/doc_clean.png` → spinner → **chassis, engine, make, model, year auto-filled** with a confidence badge.
3. Citizen fills owner name, CNIC, district, uploads a photo → **Submit** → success screen with tracking number.
4. `/track/<tracking_no>` (public, no login) shows status timeline `SUBMITTED`.
5. Logout → **Officer Login** (`officer1` / `demo123`) → `/officer`: stat cards, **district bar chart**, table with alert badges.
6. Open the planted **exact-duplicate** application → alert `DUPLICATE_EXACT` → side-by-side compare with the matching record.
7. Open the planted **near-duplicate** (e.g. `NZE141-1234567` vs `NZE141-1234S67`) → alert `DUPLICATE_NEAR` with score.
8. Open the planted **OCR-mismatch** application (typed chassis ≠ document chassis) → alert `OCR_MISMATCH`.
9. Try **Verify** on an application with an open HIGH alert → blocked with message "Resolve high-severity alerts first" → resolve alert → Verify succeeds.
10. **Request Info** on another application → citizen logs in → sees request → edits a field → responds → status returns to `UNDER_REVIEW`, alerts re-computed.
11. Officer dashboard → **Export CSV** for a district → file downloads.
12. Admin button **Reset Demo Data** (`admin1` / `demo123`) restores the seed in one click.

> Every step above gets a Phase-6 smoke test. Anything outside this list: **do not build**.

---

## 4. REPO LAYOUT (create exactly this)

```
ncp-vision/
├── PLAN.md                  # this file
├── DECISIONS.md             # Codex appends assumptions here
├── README.md                # run instructions (written in Phase 7)
├── Makefile
├── demo_assets/sample_docs/ # generated PNGs (Phase 3)
├── backend/
│   ├── requirements.txt
│   ├── uploads/             # saved files (gitignored)
│   ├── scripts/make_sample_docs.py
│   ├── tests/
│   │   ├── test_normalize.py
│   │   ├── test_duplicates.py
│   │   ├── test_anomalies.py
│   │   ├── test_ocr_parse.py
│   │   └── test_api_flow.py
│   └── app/
│       ├── main.py          # app, startup (create tables, seed if empty, load OCR), routers, static /files
│       ├── config.py        # DATABASE_URL, JWT_SECRET, UPLOAD_DIR, OCR_ENGINE (easyocr|stub)
│       ├── db.py            # engine, get_session
│       ├── models.py        # SQLModel tables
│       ├── schemas.py       # Pydantic request/response models
│       ├── auth.py          # login, JWT, role dependency
│       ├── constants.py     # districts, makes/models, enums
│       ├── seed.py          # deterministic synthetic dataset
│       ├── routers/{auth,citizen,officer,admin}.py
│       └── services/{normalize,duplicates,anomalies,analysis,ocr,tracking,audit}.py
└── frontend/
    ├── next.config.js       # rewrites /api → :8000, /files → :8000/files
    ├── lib/{api.ts,auth.ts,types.ts}
    ├── components/{Banner,StatusBadge,AlertBadge,Navbar,Timeline,CompareTable}.tsx
    └── app/
        ├── page.tsx                       # landing + track box
        ├── login/page.tsx
        ├── track/[trackingNo]/page.tsx    # public
        ├── citizen/apply/page.tsx
        ├── citizen/applications/page.tsx
        ├── citizen/applications/[id]/page.tsx   # respond to info request
        ├── officer/page.tsx               # dashboard
        └── officer/applications/[id]/page.tsx
```

`Makefile` targets (exact names): `setup`, `warm-ocr`, `seed`, `dev-backend`, `dev-frontend`, `test`.

---

## 5. DATA MODEL (SQLModel — exact names)

**Enums (strings):**
- `Role`: `citizen | officer | admin`
- `Status`: `SUBMITTED | UNDER_REVIEW | INFO_REQUESTED | PROFILE_VERIFIED | CLOSED_INCOMPLETE`
- `AlertType`: `DUPLICATE_EXACT | DUPLICATE_NEAR | MISSING_REQUIRED | NO_DOCUMENT | NO_PHOTO | YEAR_IMPLAUSIBLE | ID_FORMAT_ODD | CNIC_FORMAT | OWNER_MULTI_VEHICLE | OCR_MISMATCH | MAKE_MODEL_CONFLICT`
- `Severity`: `low | medium | high`
- `AlertState`: `open | dismissed | confirmed`
- `DocKind`: `registration_doc | photo`

**Tables:**

`User(id, username, password, full_name, role)` — plaintext password is acceptable (demo only; note in DECISIONS.md).

`Application(id, tracking_no, citizen_id→User, status, district, make, model, year, color, chassis_no, engine_no, chassis_norm, engine_norm, owner_name, owner_cnic, owner_phone, info_request_note, officer_note, risk_level, is_synthetic, created_at, updated_at)`
- `risk_level` ∈ `none | low | medium | high` (max open-alert severity; computed, never typed by a user)
- `*_norm` = output of `normalize_id()` (section 6.1), always recomputed on save.

`Document(id, application_id→Application, kind, filename, path, ocr_text, ocr_chassis, ocr_engine, ocr_confidence)` — `application_id` nullable (an upload exists before the application is submitted).

`Alert(id, application_id, type, severity, message, related_application_id nullable, score nullable, state, source)` — `source` ∈ `system`. Alert state changes only by officer action.

`AuditLog(id, actor_username, action, application_id nullable, detail, created_at)`

**Constants (`constants.py`):**
- `DISTRICTS`: Peshawar, Mardan, Swat, Abbottabad, Kohat, Bannu, Dera Ismail Khan, Swabi, Charsadda, Nowshera, Mansehra, Malakand, Buner, Dir Lower, Chitral, Haripur
- `MAKE_MODELS = {"Toyota": ["Corolla","Land Cruiser","Prado","Vitz","Aqua","Hilux","Passo"], "Honda": ["Civic","Vezel","Fit","City","N-Box"], "Suzuki": ["Alto","Wagon R","Swift","Every","Jimny"], "Nissan": ["Dayz","Note","X-Trail","Sunny"], "Daihatsu": ["Mira","Move","Tanto","Cast"]}`
- `MODEL_MIN_YEAR = {"Aqua": 2011, "Vezel": 2013, "N-Box": 2011, "Dayz": 2013}`

---

## 6. AI / LOGIC SPEC (implement exactly)

### 6.1 `services/normalize.py`
```python
def normalize_id(s: str | None) -> str:
    # 1. None/"" -> ""
    # 2. uppercase, strip, remove all chars except A-Z0-9
    # 3. return result   (DO NOT apply O->0 here; confusion handling is in duplicates)
def confusion_fold(s: str) -> str:
    # map O->0, I->1, L->1, S->5, B->8, Z->2, Q->0 ; used ONLY for near-dup comparison
```
**Important domain fact:** NCP vehicles are mostly Japanese imports. Their chassis numbers look like `NZE141-1234567` (model code + serial), NOT 17-char VINs. **Never enforce 17 characters.**

### 6.2 `services/duplicates.py`
```python
def find_duplicates(session, app) -> list[AlertDraft]
```
For every OTHER application `o` (exclude self; ignore `CLOSED_INCOMPLETE`), for each identifier pair (chassis, engine) where both norms are non-empty:
- `a == b` → **DUPLICATE_EXACT**, severity `high`, score `100`
- else `s = rapidfuzz.fuzz.ratio(confusion_fold(a), confusion_fold(b))`; if `s >= 90` and `abs(len(a)-len(b)) <= 2` → **DUPLICATE_NEAR**, severity `medium` (or `high` if `s >= 95`), score `s`
- Message example: `"Chassis NZE141-1234567 is a near match (score 94) to application NCP-KP-2026-000045."`
- One alert per (other application, identifier type). Set `related_application_id = o.id`.

### 6.3 `services/anomalies.py` — rules (each is a small pure function)

| Type | Rule | Severity |
|---|---|---|
| `MISSING_REQUIRED` | any of chassis, engine, make, model, year, owner_name, owner_cnic, district is empty | high |
| `NO_DOCUMENT` | no `registration_doc` attached | medium |
| `NO_PHOTO` | no `photo` attached | low |
| `YEAR_IMPLAUSIBLE` | year < 1980 or year > current year | medium |
| `ID_FORMAT_ODD` | chassis_norm len <6 or >20, or engine_norm len <4 or >20, or either has no digit | medium |
| `CNIC_FORMAT` | owner_cnic not matching `^\d{5}-\d{7}-\d$` | medium |
| `OWNER_MULTI_VEHICLE` | same `owner_cnic` appears on ≥ 3 applications | medium |
| `MAKE_MODEL_CONFLICT` | model not in `MAKE_MODELS[make]`, OR year < `MODEL_MIN_YEAR[model]` | medium |
| `OCR_MISMATCH` | for a `registration_doc` with `ocr_confidence >= 0.5`: `fuzz.ratio(typed_norm, ocr_norm) < 90` for chassis or engine → **high**; `90–99` → **low** ("typing variation") | high / low |

### 6.4 `services/analysis.py`
```python
def analyze(session, application_id) -> None:
    # 1. delete this application's alerts where source == "system" AND state == "open"
    #    (keep dismissed/confirmed ones as history)
    # 2. run find_duplicates + all anomaly rules
    # 3. skip creating an alert if an identical (type, related_application_id, state != open) already exists
    # 4. insert alerts
    # 5. set application.risk_level = max severity among OPEN alerts (none if zero)
```
Call `analyze()` on: submit, respond, seed (for every seeded application), and `POST /officer/applications/{id}/reanalyze`.

### 6.5 `services/ocr.py`
```python
def extract(image_path: str) -> dict:
    # returns {"chassis_no","engine_no","make","model","year","confidence","raw_text"}  (missing -> None)
```
- Reader created once: `easyocr.Reader(["en"], gpu=False)`, stored module-level, initialised in `main.py` startup.
- Preprocess: open with OpenCV, downscale so max side ≤ 1600px, convert to grayscale, `cv2.fastNlMeansDenoising` OR skip if slow. Keep it simple.
- Run `reader.readtext(img)` → join lines with `\n` → `raw_text`. `confidence` = mean of line confidences.
- **Label-based regex parsing** (case-insensitive, allow `:` or `-` or space after label):
  - `chassis(?:\s*no\.?|\s*number)?` → chassis
  - `engine(?:\s*no\.?|\s*number)?` → engine
  - `make` → make; `model` → model; `(?:model\s*year|year|mfg\.?\s*year)` → year (4 digits)
  - If make not labelled, scan text for any key of `MAKE_MODELS`.
- Fuzzy-fix labels that OCR mangles (e.g. `Chassls`) using `rapidfuzz.process.extractOne` against label list with cutoff 80.
- `OCR_ENGINE=stub` (config, **tests only**) returns all `None` with confidence `0.0`. Never use stub in the demo.
- Wrap everything in try/except → on any error return all `None`, `confidence 0.0`.

### 6.5b Sample documents — `backend/scripts/make_sample_docs.py`
Use Pillow to draw clean, high-contrast, black-on-white "registration/import document" images (≈1200×800, DejaVuSans font) with labelled lines:
```
IMPORT / REGISTRATION DOCUMENT  (SYNTHETIC DEMO)
Make: Toyota
Model: Corolla
Model Year: 2014
Chassis No: NZE141-1234567
Engine No: 1NZ-A123456
```
Generate into `demo_assets/sample_docs/`:
- `doc_clean.png` — unique identifiers (no match in seed) → happy path
- `doc_exact_dup.png` — chassis+engine identical to seeded record `SEED-DUP-EXACT-1`
- `doc_near_dup.png` — chassis differs by one character from a seeded record
- `doc_mismatch.png` — used by the demo operator who deliberately types a *different* chassis in the form
- `doc_noisy.png` — slight rotation (2°), gaussian noise, lower contrast (OCR robustness demo)
- `photo_vehicle.png` — plain grey placeholder rectangle with text "VEHICLE PHOTO (SYNTHETIC)"

Seed values for the `doc_*` identifiers MUST be defined in one place (`constants.py: DEMO_IDS`) and used by BOTH the script and `seed.py`.

### 6.6 Status machine (enforce server-side; invalid transition → HTTP 409)

| Action (officer) | From → To | Rules |
|---|---|---|
| `start_review` | SUBMITTED → UNDER_REVIEW | |
| `request_info` | SUBMITTED/UNDER_REVIEW → INFO_REQUESTED | `note` required |
| `verify` | UNDER_REVIEW → PROFILE_VERIFIED | **blocked (409) if any OPEN alert has severity `high`** |
| `close_incomplete` | any non-final → CLOSED_INCOMPLETE | `note` required |
| *(citizen)* `respond` | INFO_REQUESTED → UNDER_REVIEW | citizen may edit fields; re-run `analyze()` |

Every action writes an `AuditLog` row. Alert resolution (`dismissed` / `confirmed`) also writes one and also re-computes `risk_level`.

### 6.7 `seed.py` (deterministic: `random.Random(42)`)
Create users: `citizen1`, `citizen2` (role citizen), `officer1` (officer), `admin1` (admin) — all password `demo123`.
Create **240** applications, all `is_synthetic=True`, owner CNICs like `99999-NNNNNNN-N` (`99999` prefix = obviously fake), names from a fixed list, spread across all districts, mixed statuses (≈50% SUBMITTED, 25% UNDER_REVIEW, 10% INFO_REQUESTED, 10% PROFILE_VERIFIED, 5% CLOSED_INCOMPLETE). Plant, with comments in code:
- 8 exact duplicate pairs (second copy: same chassis, same/different engine)
- 10 near-duplicate pairs (1-char substitution; 4 of them use O/0 or S/5 confusion)
- 12 applications missing 1–2 required fields
- 6 with `YEAR_IMPLAUSIBLE`
- 5 CNICs reused on 3+ applications
- 8 `MAKE_MODEL_CONFLICT`
- the specific `DEMO_IDS` records the sample docs reference
- 1 application in `UNDER_REVIEW` with a planted `OCR_MISMATCH` (attach `doc_mismatch`-style Document row with `ocr_chassis` differing from typed chassis — insert OCR fields directly, no OCR run in seed)
After inserting, call `analyze()` for each. Print summary counts. Seed runs on startup only if the `User` table is empty; `POST /api/admin/reset` drops all tables, recreates, reseeds.

---

## 7. API CONTRACT (exact paths; JSON unless noted; auth = `Authorization: Bearer <jwt>`)

| Method & Path | Role | Request → Response |
|---|---|---|
| `POST /api/auth/login` | public | `{username,password}` → `{token, role, full_name}` |
| `GET  /api/track/{tracking_no}` | public | → `{tracking_no, status, district, make, model, year, updated_at, timeline:[{status,at}], info_request_note}` (NO personal data) |
| `POST /api/uploads` | citizen | multipart `file`, `kind` → `{upload_id, kind, url, ocr: {chassis_no,engine_no,make,model,year,confidence} \| null}` (OCR only when `kind=registration_doc`) |
| `POST /api/applications` | citizen | `{district,make,model,year,color,chassis_no,engine_no,owner_name,owner_cnic,owner_phone,upload_ids:[int]}` → `{id, tracking_no, status}`; sets `SUBMITTED`, runs `analyze()` |
| `GET  /api/applications/mine` | citizen | → list |
| `GET  /api/applications/{id}` | citizen (own) | → full application + docs + `info_request_note` (alerts hidden from citizen) |
| `POST /api/applications/{id}/respond` | citizen (own) | `{fields to update, message}` → updated app |
| `GET  /api/officer/applications` | officer/admin | query: `status, district, q (searches tracking_no/chassis/engine/owner_name/cnic), min_risk, page, page_size` → `{items, total}` |
| `GET  /api/officer/applications/{id}` | officer/admin | → app + documents + alerts (with `related` summary of the other application) + audit log |
| `POST /api/officer/applications/{id}/action` | officer/admin | `{action, note?}` → updated app (409 on invalid) |
| `POST /api/officer/alerts/{id}/resolve` | officer/admin | `{resolution: "dismissed"\|"confirmed", note?}` |
| `POST /api/officer/applications/{id}/reanalyze` | officer/admin | → alerts |
| `GET  /api/officer/stats` | officer/admin | → `{totals:{total,open_alerts,high_risk}, by_status:{}, by_district:[{district,total,high_risk,verified}], alerts_by_type:{}}` |
| `GET  /api/officer/report.csv?district=` | officer/admin | CSV download: tracking_no, district, make, model, year, status, risk_level, open_alerts |
| `POST /api/admin/reset` | admin | reset + reseed → `{ok:true}` |
| `GET  /files/{path}` | static | uploaded files |

Tracking number: `NCP-KP-{year}-{id:06d}`, generated in `services/tracking.py`.
Role guard: a FastAPI dependency `require_role(*roles)`; wrong role → 403.

---

## 8. FRONTEND SPEC

- **Style:** Tailwind only. Clean, government-dashboard feel. Colors: status badges (SUBMITTED grey, UNDER_REVIEW blue, INFO_REQUESTED amber, PROFILE_VERIFIED green, CLOSED_INCOMPLETE slate); alert severity (high red, medium amber, low yellow).
- `Banner.tsx` rendered in root `layout.tsx` on every page (text from Golden Rule 8).
- `lib/auth.ts`: store `{token, role, full_name}` in `localStorage`; `lib/api.ts`: `fetch` wrapper that adds the header and redirects to `/login` on 401.
- **Route guards:** a tiny `useRequireRole()` hook at the top of citizen/officer pages.
- **`/citizen/apply`** — 3 steps in one page (component state, no router):
  1. Upload document (file input) → call `/api/uploads` → show spinner "Reading document…" → show extracted fields with a confidence badge; every field remains editable.
  2. Owner + district + color + phone, optional photo upload.
  3. Review summary → Submit → success card with tracking number + link to `/track/...`.
- **`/officer`** — 4 stat cards, bar chart (`recharts` `BarChart`, X=district, bars: total & high_risk), filter row (status, district, search box, min risk), table (tracking_no, district, vehicle, status badge, risk badge, open-alert count, updated_at) with click-through, **Export CSV** button (uses current district filter), admin-only **Reset Demo Data** button with confirm dialog.
- **`/officer/applications/[id]`** — left: fields + documents (image preview via `/files/...`); right: alerts list, each with severity badge, message, **Dismiss / Confirm** buttons; for duplicate alerts a `CompareTable` showing both applications' chassis/engine/make/model/year/owner side by side with differing characters highlighted; action buttons (Start Review, Request Info [note modal], Verify, Close Incomplete [note modal]); audit timeline at bottom. Show server error messages (e.g., the 409 text) in a red toast/inline box.
- Loading + error states on every fetch (simple text is fine).
- No i18n, no dark mode, no animations, no mobile polish beyond Tailwind defaults.

---

## 9. PHASES (execute in order; each ends with VERIFY)

### Phase 1 — Scaffold (≈20 min)
- Create repo layout, `Makefile`, `requirements.txt`, Next.js app (`npx create-next-app@14 frontend --ts --tailwind --app --no-src-dir --eslint --import-alias "@/*"`), install `recharts`.
- Backend: `main.py` with `GET /api/health` → `{ok:true}`; `config.py`; `db.py`.
- `next.config.js` rewrites for `/api/*` and `/files/*`.
- **VERIFY:** `make dev-backend` + `curl localhost:8000/api/health` → `{"ok":true}`; `make dev-frontend` loads `/` with the banner; `curl localhost:3000/api/health` (via proxy) works.

### Phase 2 — Models, auth, seed (≈5 min)
- Implement `models.py`, `constants.py`, `auth.py`, `routers/auth.py`, `services/{normalize,tracking,audit}.py`, `seed.py` (without calling analyze yet — stub it).
- **VERIFY:** `pytest tests/test_normalize.py` (cases: `"nze141-1234 567"→"NZE1411234567"`, `None→""`, `confusion_fold("1NZ-O123")` stable); login returns a token for all 4 users; DB has 240 applications.

### Phase 3 — Detection engines + tests (≈5 min) ⭐ core of the demo
- Implement `duplicates.py`, `anomalies.py`, `analysis.py`; wire `analyze()` into seed.
- Write `test_duplicates.py` (exact, near, O/0, S/5, unrelated=no alert, length-gap guard) and `test_anomalies.py` (one test per rule).
- **VERIFY:** `pytest` green; after `make seed`, SQL count: `DUPLICATE_EXACT ≥ 8`, `DUPLICATE_NEAR ≥ 10`, `MISSING_REQUIRED ≥ 12`, `OCR_MISMATCH ≥ 1`. Print the counts.


HARD DEADLINE: 10 minutes total. Phases 1-3 are done. Ignore PLAN.md phases 4-7.
RULES: no tests, no pytest, no refactors, no questions, no new libraries, no OCR.
Commit after each step. If a step overruns, ship what runs and move on.
Banner on every page: "DEMO - synthetic data. Profiling is not registration, customs clearance, or eligibility for any scheme."

STEP A (5 min) - Officer side [ship this first]
Backend routers/officer.py (officer/admin roles only):
- GET /api/officer/applications?status=&district=&q= -> {items,total}
- GET /api/officer/applications/{id} -> app + alerts (include related app summary) 
- POST /api/officer/applications/{id}/action {action,note?}: start_review, request_info, verify, close_incomplete. verify returns 409 "Resolve high-severity alerts first" if any open high alert. Write an AuditLog row.
- POST /api/officer/alerts/{id}/resolve {resolution: dismissed|confirmed}; recompute risk_level.
- GET /api/officer/stats -> totals, by_status, by_district
Frontend:
- /login: username/password, redirect officer -> /officer, citizen -> /citizen/apply. Store token in localStorage.
- /officer: stat cards, filters (status, district, search), table with status + risk badges, row click -> detail.
- /officer/applications/[id]: fields left; alerts right with Dismiss/Confirm; plain 2-column compare table for duplicate alerts; action buttons; show server errors in red.
No charts, no CSV, no audit UI.

STEP B (3 min) - Citizen submit
- POST /api/applications (citizen role) -> sets SUBMITTED, runs analyze(), returns {id, tracking_no}
- GET /api/track/{tracking_no} public -> status + vehicle basics only
- Pages: / (links + track box), /citizen/apply (one plain form with all fields, submit, success card with tracking number), /track/[trackingNo]
- No file uploads.

STEP C (2 min) - Ship
- README.md: how to run both servers, logins (citizen1 / officer1 / admin1, password demo123).
- Run the app once and fix only crashes.

CUT: OCR, uploads, respond loop, CSV, charts, citizen list page, admin reset, audit UI, tests.