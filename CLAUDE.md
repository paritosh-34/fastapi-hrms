# FastAPI HR system tutorial

This folder holds a three-file HTML tutorial that teaches FastAPI to frontend-heavy JS developers by building an **HR / team-ops API**. There is no companion code repo: the three pages are the whole deliverable, and their snippets are hand-authored rather than generated from a running project. The full agreed plan is in [docs/COURSE_PLAN.md](docs/COURSE_PLAN.md). Read it before building anything.

## Audience
- Frontend-heavy full-stack devs with about 5 years of experience, writing React and TypeScript daily. A friend following along has used Python very little.
- Express knowledge is **intermediate**: routes, `express.Router`, middleware, `req.body`, error-handling middleware. Assume nothing about custom middleware chains or Express internals.
- **Never reference NestJS.** There is no NestJS experience. Jest is the testing comparison; supertest is not.
- Teach by mapping Express concepts to FastAPI ones (side-by-side code). Skip Python fundamentals; they live in the separate cheatsheet. Decorators need no explanation beyond a nod to TS decorators.
- Use typed Python throughout.

## Structure
- `python-for-js-devs.html` — a lookup cheatsheet, not a lesson. Anchored rows so the tutorial can deep-link into it.
- `part-1-employees-api.html` — chapters 0–5: a DB-backed employees and departments API.
- `part-2-auth-leave-tests.html` — chapters 6–11: auth with three roles, leave requests and approvals, errors, tests, agent-ready OpenAPI.

## Teaching rules
- **The tutorial is build-driven. No theory chapters.** Chapter 0 ships a running endpoint; every later chapter ships real endpoints.
- Theory arrives three ways only: one-line **syntax chips** linking to a cheatsheet anchor; **"Why this is different" boxes**, reserved for what Express genuinely lacks (no `req, res`; type hints as the validation layer; `Depends`; `response_model` filtering output; Pydantic validating at the boundary; blocking calls inside `async def`); and otherwise just showing the code with a half-sentence comparison.
- Because the frontend is React, lean into what a client consumes: response shapes, CORS, parseable error payloads, and generating a typed TS client from `/openapi.json`.

## Style
- Match the art style of the reference page: `/Users/paritoshbatish/Downloads/AI infused learning/class 1-2 foundations.html`. Read it for its CSS tokens and components before writing a page.
- Key traits: warm paper background (`--paper:#fdf7f0`), orange accent (`--orange:#ff5b35`), with teal, blue, gold, purple and pink tints. Fonts are Fraunces (headings), Manrope (body) and JetBrains Mono (code/labels). It has a fixed progress bar, a sticky top nav that appears on scroll, a hero with an interactive card, numbered `section.block`s with `.sec-num` badges, and `.def`, `.wow`, `.analogy.<color>`, `.note` and dark `.industry` callout boxes. Code blocks are dark (`--code-bg:#211c18`) with syntax-highlight spans.
- Each page is a single self-contained HTML file with inline CSS and JS. Google Fonts are the only external resource.
- A tracker on the page counts shipped endpoints ("7 of 24 endpoints").

## Database
Local SQLite file `app.db` via `aiosqlite`, gitignored, WAL mode on so a GUI can read it while the server runs. Inspected with the VS Code SQLite Viewer extension, the `sqlite3` CLI, or DB Browser for SQLite. A `seed.py` wipes and repopulates known data. SQLite's concurrency limits are taught, not hidden: chapter 8 fixes the leave-balance race with an atomic conditional `UPDATE` and names what Postgres would do differently.

## Downstream use
A chat agent will later be built on top of this backend, as a chat window in the user's own React frontend, performing CRUD as the user talks to it. It is not part of this tutorial. Endpoint descriptions and OpenAPI output must therefore be clean, because they become the agent's tool schemas, and authorization must be enforced per caller inside the API rather than left to the agent layer. The React frontend is the user's own work and needs no tutorial. A later, separate page will cover production code for high scalability.
