# Course plan: FastAPI for JS/React developers

Agreed on 2026-11-04. Domain switched from e-commerce to an **HR / team-ops system** on the same day, because the real goal downstream is a chat agent that performs CRUD as the user talks to it, and HR is the domain where that agent has to resolve people and dates from ambiguous language and enforce *per-caller* authorization inside every tool call.

Three self-contained HTML files. The tutorial is build-driven: chapter 0 ships a running endpoint, and every chapter after it ships real endpoints of the HR API. There are no theory chapters.

## Build order and status

As of 2026-11-04:

| File | Status |
|---|---|
| `python-for-js-devs.html` | **Built.** 27 anchored lookup rows across 13 sections, live filter box, contents sidebar. |
| `part-1-employees-api.html` | **Built.** 6 chapters, endpoints 1-12, 4 why-different boxes, ~181 KB. |
| `part-2-auth-leave-tests.html` | **Built.** 6 chapters, endpoints 13-24, 2 why-different boxes, ~198 KB. |

`docs/STYLE_TOKENS.css` holds an extracted copy of the style reference's tokens and component
list, so the visual contract survives the reference file being moved or renamed.

Build in this order, because it keeps the three pages visually consistent:

1. **`python-for-js-devs.html`** first. It is the smallest page, and writing it first pins down the shared CSS token set and callout components that both tutorial pages then reuse verbatim.
2. **`part-1-employees-api.html`**.
3. **`part-2-auth-leave-tests.html`**.

Before writing the first page, read the style reference at `/Users/paritoshbatish/Downloads/AI infused learning/class 1-2 foundations.html` in full and extract its CSS custom properties and component classes. The three pages here must look like siblings of it.

## Files

| File | Role |
|---|---|
| `python-for-js-devs.html` | A cheatsheet, not a lesson. Lookup-oriented, JS left / Python right, anchored rows so the tutorial can deep-link into it. Kept open in a second tab. |
| `part-1-employees-api.html` | Chapters 0–5. Ends with a working, DB-backed employees + departments API. |
| `part-2-auth-leave-tests.html` | Chapters 6–11. Ends with a tested, agent-ready backend. |

### Cheatsheet contents
dicts/lists vs objects/arrays, f-strings, comprehensions as `map`/`filter`, `None` and truthiness, imports, minimal classes, `try/except`, `str | None`, `list[int]`, `Literal`, `Annotated`, enums, and a gotchas block (indentation, `dict["k"]` raises `KeyError` so use `.get()`, mutable default arguments, no `===`). Types are erased at runtime *except* that FastAPI and Pydantic read them to validate requests.

## How theory is delivered

No theory sections. Three mechanisms only:

1. **Syntax chips** — one inline line linking to a cheatsheet anchor, e.g. `# new: f-string -> cheatsheet`.
2. **"Why this is different" boxes** — reserved for things Express genuinely does not have. There are about six in the whole course: no `req, res` (you declare parameters and return data); type hints *are* the validation layer; `Depends`; `response_model` filtering the output; Pydantic validating at the boundary rather than inside the handler; blocking calls inside `async def`.
3. **Everything else is just shown** — if it works like Express, it gets a half-sentence comparison and the build moves on.

A tracker on the page counts shipped endpoints ("7 of 24 endpoints"), which is honest here because every chapter adds some.

## Domain model

- **Department** — name, description.
- **Employee** — name, email, `role` (`employee` | `manager` | `hr_admin`), job title, hire date, salary, employment status, `department_id`, and a self-referential `manager_id`.
- **LeaveBalance** — per employee, leave type and year: entitled days and used days. Stored rather than computed, because the stored row is what makes the approval race condition real.
- **LeaveRequest** — employee, leave type, start/end date, working days, reason, `status` (`draft` | `submitted` | `approved` | `rejected` | `cancelled`), decided-by and decided-at.

## Part 1: the employees API

| # | What you ship | Theory that earns its place |
|---|---|---|
| 0 | `GET /health` running under `uvicorn --reload`, `/docs` open in a browser | venv and pip in about half a screen, rest deferred to the cheatsheet; a short box on `uv`. **Why different:** no `req, res` — you declare parameters and return data |
| 1 | `GET /employees`, `GET /employees/{id}` over in-memory data; typed path and query params; `HTTPException` 404 | **Why different:** the type hint is the validator. Express needs Zod wired in by hand |
| 2 | `POST /employees` with a Pydantic body, `Field` constraints, separate `EmployeeCreate` / `EmployeeRead`, `response_model` hiding salary and password hash | Pydantic is Zod attached to the function signature. **Box:** `/openapi.json` generates a typed TS client for the React app |
| 3 | The same endpoints on SQLite via SQLAlchemy 2.0 (`Mapped[]`, async session), plus departments and the `manager_id` self-relationship; `PATCH` and `DELETE` | **Why different:** `Depends` and `get_db`. Also the trap of blocking calls inside `async def` |
| 4 | Filtering by department, role and status; search by name or email; sorting; pagination; a response envelope | Dependencies compose and are cached per request; a params class as a reusable dependency |
| 5 | The single file split into `routers/`, `schemas/`, `models/`, `services/`; `pydantic-settings`; CORS for the React dev server; WAL mode; `seed.py` | `APIRouter` is `express.Router`; when a real middleware beats a `Depends` |

## Part 2: auth, leave and tests

| # | What you ship | Theory that earns its place |
|---|---|---|
| 6 | Registration, form-encoded login, password hashing, JWT, `get_current_user`, `GET /me`, a `require_role` dependency, and salary visible only to the owner, their manager and HR admins | `OAuth2PasswordBearer`, why the login body is form-encoded, authorization by stacking dependencies, field-level filtering per caller |
| 7 | Leave requests: create a draft, edit it, submit it, list your own; leave balances; overlap validation; working-day calculation | Why this logic belongs in a service rather than the route |
| 8 | Manager approve and reject, scoped so only the requester's manager or an HR admin can decide; status change and balance decrement in one transaction | Transactions, and the double-approval race that overdraws a leave balance — demonstrated, then fixed with an atomic conditional `UPDATE ... WHERE used_days + :days <= entitled_days`. A box on what changes under Postgres with `SELECT ... FOR UPDATE` |
| 9 | Domain exceptions mapped to status codes, custom exception handlers, one consistent error body the React app can parse, request logging | `HTTPException` vs exception handlers vs Express error middleware |
| 10 | pytest with `httpx.AsyncClient`, fixtures, `dependency_overrides` pointing at a test database, per-role auth fixtures, and a test that proves the chapter 8 race is fixed | Jest is the comparison; supertest is not assumed |
| 11 | `summary`, `description`, `operation_id`, tags and examples, so the OpenAPI output reads cleanly as agent tool schemas | Why those descriptions become the agent's tool definitions; why the agent must run *as* the user rather than as an admin; the shape of a confirmation step for destructive tools. Then a preview-only list: Postgres with Alembic, Docker, Redis, background jobs, rate limiting, and SSE for the later chat endpoint |

## Technical decisions

- **Async from the start.** It matches the Node mental model, and the later agent makes async LLM calls. The blocking-call trap is covered in chapter 3.
- **SQLAlchemy 2.0, not SQLModel.** Production standard, fully typed with `Mapped[]`.
- **SQLite file, not Postgres.** `app.db` through `aiosqlite`, gitignored, WAL mode on so a GUI can read it while the server holds it. Inspected with the VS Code SQLite Viewer extension, the `sqlite3` CLI, or DB Browser for SQLite. A `seed.py` wipes and repopulates known data, which matters once the agent is being tested against destructive requests.
- **SQLite's concurrency limits are taught, not hidden.** No `SELECT ... FOR UPDATE`; writers serialize. Chapter 8 therefore fixes the race with a single atomic conditional `UPDATE`, which is the more portable lesson, and names what Postgres would do differently.
- **Chapter 11 is a preview.** Full production and high-scalability content is a separate, later page.

## Audience calibration

- Frontend-heavy full-stack developers with **intermediate** Express knowledge: routes, `express.Router`, middleware, `req.body`, error-handling middleware. Nothing assumes custom middleware chains or Express internals.
- **No NestJS references anywhere.** No prior NestJS experience exists.
- Jest is the testing reference point; supertest is not.
- Because the frontend is React, the course leans into what a client consumes: response shapes, CORS, parseable error payloads, and generating a typed TS client from the OpenAPI schema.

## Downstream, not part of this tutorial

- **The agent.** A chat window in the React frontend that performs CRUD as the user talks to it. The reason the OpenAPI output and endpoint descriptions have to be clean, and the reason per-caller authorization is taught in chapters 6 and 8 rather than left to the agent layer.
- **The React frontend.** The user builds it; no tutorial for it. The backend only has to make it easy: CORS, clean response shapes, and room for SSE streaming later.

## Decided: no companion code

There is no runnable `hr-api/` project. The three HTML pages are the whole deliverable and their snippets are hand-authored. Consequences to work against deliberately:

- Snippets are unverified, so later chapters drift most easily. Keep the running code visibly cumulative, state the full file path above every block, and re-show whole files at the points where they change shape (chapters 3, 5 and 8) instead of only showing diffs.
- Chapter 10's tests are illustrative rather than proven to pass. Keep them simple enough to be obviously correct by reading.
- Any version-sensitive API (SQLAlchemy 2.0 `Mapped[]`, Pydantic v2, `pydantic-settings`) should be pinned to exact versions in the chapter 0 requirements block, so a reader's `pip install` matches what the pages show.

---

# Decisions locked at build time (2026-11-04)

These were open in the plan above and are now pinned, because three pages written
independently will otherwise drift. Changing any of them means editing the pages.

## Endpoint inventory — the tracker's denominator

The plan promised a tracker reading "7 of 24 endpoints" without saying what the 24 were.
They are these, and the two parts split 12/12.

### Part 1 (ids 1–12)

| # | Ch | Endpoint |
|---|---|---|
| 1 | 0 | `GET /health` |
| 2 | 1 | `GET /employees` |
| 3 | 1 | `GET /employees/{employee_id}` |
| 4 | 2 | `POST /employees` |
| 5 | 3 | `PATCH /employees/{employee_id}` |
| 6 | 3 | `DELETE /employees/{employee_id}` |
| 7 | 3 | `GET /departments` |
| 8 | 3 | `POST /departments` |
| 9 | 3 | `GET /departments/{department_id}` |
| 10 | 3 | `PATCH /departments/{department_id}` |
| 11 | 4 | `GET /employees/{employee_id}/reports` |
| 12 | 4 | `GET /departments/{department_id}/employees` |

### Part 2 (ids 13–24)

| # | Ch | Endpoint |
|---|---|---|
| 13 | 6 | `POST /auth/register` |
| 14 | 6 | `POST /auth/login` |
| 15 | 6 | `GET /me` |
| 16 | 7 | `POST /leave-requests` |
| 17 | 7 | `GET /leave-requests` |
| 18 | 7 | `GET /leave-requests/{request_id}` |
| 19 | 7 | `PATCH /leave-requests/{request_id}` |
| 20 | 7 | `POST /leave-requests/{request_id}/submit` |
| 21 | 7 | `POST /leave-requests/{request_id}/cancel` |
| 22 | 7 | `GET /me/leave-balances` |
| 23 | 8 | `POST /leave-requests/{request_id}/approve` |
| 24 | 8 | `POST /leave-requests/{request_id}/reject` |

Cumulative tracker values per chapter: **1, 3, 4, 10, 12, 12 · 15, 22, 24, 24, 24, 24.**
Chapters 5, 9, 10 and 11 ship no new endpoints, which the tracker shows honestly by not moving.

## Pinned versions

The plan required exact pins in chapter 0 so a reader's `pip install` matches the pages.

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
email-validator==2.2.0
pydantic-settings==2.7.0
sqlalchemy==2.0.36
aiosqlite==0.20.0
# part 2 adds:
pyjwt==2.10.1
bcrypt==4.2.1
python-multipart==0.0.20
pytest==8.3.4
pytest-asyncio==0.25.0
httpx==0.28.1
```

**PyJWT and bcrypt directly, not python-jose or passlib.** python-jose is effectively
unmaintained, and passlib's bcrypt backend emits a version-detection warning against
bcrypt 4.x that would cost a paragraph of explaining in a tutorial about something else.

## Package layout as of chapter 5

Part 2 extends this. It does not reorganise it.

```
hr-api/
├── .env  ├── .gitignore  ├── requirements.txt  ├── seed.py  ├── app.db
└── app/
    ├── __init__.py  ├── main.py  ├── deps.py        # get_db, CurrentUser, require_role
    ├── core/     __init__.py, config.py, db.py      # + security.py (6), errors.py (9)
    ├── models/   __init__.py, base.py, department.py, employee.py   # + leave.py (7)
    ├── schemas/  __init__.py, common.py, department.py, employee.py # + auth.py (6), leave.py (7)
    ├── services/ __init__.py, employees.py                          # + leave.py (7)
    └── routers/  __init__.py, health.py, employees.py, departments.py # + auth.py (6), leave.py (7)
└── tests/  conftest.py, test_auth.py, test_employees.py, test_leave.py  # (10)
```

Layering is one-way — routers → services → models — because circular imports are a
startup crash in Python, not a resolved cycle.

## Domain model field names

- `Role`: `employee` | `manager` | `hr_admin`
- `EmploymentStatus`: `active` | `on_leave` | `terminated`
- `LeaveType`: `annual` | `sick` | `unpaid`
- `LeaveStatus`: `draft` | `submitted` | `approved` | `rejected` | `cancelled`
- All four are `class X(str, Enum)`, so a member *is* a string and serialises without conversion.
- `Employee.password_hash` exists as a column from chapter 3 and is never returned;
  chapter 6 is where it starts being set.

## Budget for "Why this is different" boxes

The plan allowed about six in the whole course. Allocated:

| # | Box | Page · chapter |
|---|---|---|
| 1 | No `req, res` — you declare parameters and return data | Part 1 · 0 |
| 2 | The type hint *is* the validation layer | Part 1 · 1 |
| 3 | `Depends` and `get_db` | Part 1 · 3 |
| 4 | Blocking calls inside `async def` | Part 1 · 3 |
| 5 | Authorization by stacking `Depends` | Part 2 · 6 |
| 6 | `response_model` filters the output | Part 2 · 6 |

Pydantic-validates-at-the-boundary, listed in the plan as a candidate, is covered
inside box 2 rather than taking a seventh slot.

## Shared page chrome

- The cheatsheet uses a **permanently sticky `#deck`** (brand, live filter, row count),
  because a lookup page must never hide its search. The two tutorial pages use the
  reference page's **scroll-triggered `#topnav`**.
- All three pages carry an identical **contents sidebar**: off-canvas with a toggle and
  scrim below 1400px, permanent and body-shifting at 1400px and above, built from the DOM
  (`section.block[id]` plus `.crow[id]` on the cheatsheet / `h3[id]` on the tutorial pages)
  with an IntersectionObserver marking the current entry.
- Both tutorial pages carry the endpoint tracker pill, driven by a `data-shipped` attribute
  on each `section.block`.

## Accepted deviation: when the file split happens

The plan described chapter 5 as "the single file split into `routers/`, `schemas/`,
`models/`, `services/`". The build instead splits in two stages:

- **Chapters 0-2** are genuinely one file, `app/main.py`.
- **Chapter 3**, when the database arrives, pushes the engine, the models and the schemas
  into three flat modules (`app/db.py`, `app/models.py`, `app/schemas.py`), leaving every
  route in `main.py`.
- **Chapter 5** turns those four flat modules into the package layout above.

Reason: chapter 3 is required to re-show whole files, and a single `main.py` holding engine
setup, two models, four schemas and ten routes is a ~300-line block in a dark code box.
Two stages keep every re-show readable and match what a developer actually does. Chapter 5's
opening was reworded to match, so it no longer claims a single file.

## Bug caught in review and fixed

`GET /employees/{employee_id}` was written with `response_model=EmployeeRead | EmployeeReadWithSalary`.
Because `EmployeeReadWithSalary` subclasses `EmployeeRead`, the richer object validates
cleanly against the narrower union member, so Pydantic would have **silently dropped
`salary` for exactly the callers allowed to see it** - the owner, their manager and
`hr_admin`. The field-level-filtering lesson would have taught a rule that does not fire.

Replaced with `response_model=None` plus a return annotation and a `responses={200: ...}`
entry: the route builds the correct narrow model itself, both shapes stay documented in
`/openapi.json` for the generated TS client, and the guarantee no longer depends on how a
union resolves. The surrounding prose now explains that subtlety instead of asserting that
smart-union keeps the richer model.

## Still open for review

1. **Chapter 5 carries four unrelated concerns** — package split, `pydantic-settings`,
   CORS, WAL, `seed.py`. It is the heaviest chapter in Part 1 and a candidate for splitting,
   or for moving CORS up to chapter 2 where the typed-TS-client box already lives.
2. **Part 2 is the heavier page**, holding both hard chapters (8's race, 10's tests).
   Deliberate — Part 1 is the gentle on-ramp — but worth confirming.
3. **Chapter 11 mixes three things**: OpenAPI polish, agent authorization philosophy, and
   a production preview list. The agent-authorization material is the most valuable content
   in the course for the downstream chat agent and currently sits late in the chapter.
