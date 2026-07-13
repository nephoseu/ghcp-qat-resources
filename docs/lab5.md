# Lab 5 Generating Test Data & Building a Test Harness with GitHub Copilot

## Overview

You are QA on the TaskDesk modernisation project. The legacy **TaskDesk Classic '03**
system is being retired, and its replacement — a modern FastAPI service — is going
live. The new API works, but it has zero automated tests, and migration day is coming:
every ticket sitting in the legacy system has to move across, warts and all.

Your job in this lab is to build the test data and the test harness the new API needs
before that happens: fixtures that don't duplicate login logic, factories that
understand the new API's business rules, parametrised tests that pin down its
rulebook, and a migration rehearsal against a real (if messy) legacy export.

**Estimated time:** 45 minutes

!!! tip "Download the app first"
    Lab 5 uses **TaskDesk API Modern **. Download and unzip it before following
    the setup steps below.

    [Download taskdesk-api-modern.zip](https://github.com/nephoseu/ghcp-qat-resources/releases/latest/download/taskdesk-api-modern.zip){ .md-button }

---

## Background

Functional tests need data, and modern systems make that harder than it looks. A
legacy ticket system might have let you write straight to a database table. A
modernised API enforces business rules instead: a ticket needs a real category, it can
only move through its status workflow in certain directions, and resolving one needs a
paper trail.

That means test data can't just be `Faker()` plus a dict anymore. Creating **one**
valid ticket now requires knowing which categories exist. Getting a ticket into a
**specific state** — say, `resolved` — means walking it through every legal transition
first, in the right order, with the right side effects along the way. Hand-written,
one-off fixtures don't survive contact with a system like this; they collapse under
their own duplication the moment a second test needs a ticket in a different state.

This is exactly the problem a **test harness** and **data factories** solve: shared
fixtures for the boring, repetitive tasks (auth, cleanup), and factory functions that
know how to build valid or deliberately invalid data on demand. Once you have
both, generating the data for tomorrow's migration rehearsal is just another factory
call away.

---

## Setup

### 1. Enter the project and create a virtual environment

```bash
cd src/ticket-api-modern

python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Seed data and start the API

```bash
python seed.py
uvicorn app.main:app --host 0.0.0.0 --port 8081
```

### 4. Start the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

In a second terminal, verify:

```bash
curl http://localhost:8080/health
```

You should get `{"status":"ok"}`.

!!! note "Accounts"

    | Username | Password | Role |
    |----------|----------|------|
    | `user` | `user` | Regular user |
    | `admin` | `admin` | Admin |
---

## API notes for this lab

!!! note
      The interactive docs are at **http://localhost:8080/docs** — use them to explore the
      endpoints before writing tests.

| Endpoint | Notes |
|----------|-------|
| `POST /auth/login` | Form-encoded `username`, `password`; returns a bearer token |
| `GET /categories/` | Auth required; lists all categories |
| `POST /categories/` | **Admin only** — `403` for a regular user |
| `POST /tickets/` | Requires a valid `category_id`; `severity` defaults to `medium`; invalid severity → `400`; unknown `category_id` → `404` |
| `GET /tickets/` | **Paginated** (`limit`/`offset` query params, default `limit=20`), **oldest-first** — "preserves TaskDesk Classic ordering for backwards compatibility" |
| `GET /tickets/search?q=` | Case-insensitive title substring search — **not paginated** |
| `PATCH /tickets/{id}/status` | Enforces the status workflow below (`409` if illegal); owner-only |
| `POST /tickets/{id}/comments` | Add a comment; owner or admin |
| `GET /tickets/{id}/comments` | List comments; owner or admin |
| `DELETE /tickets/{id}` | Owner-only |

!!! note "The status workflow"
    Legal transitions:

    - `open → in_progress`
    - `in_progress → resolved` (requires **at least one comment** already on the ticket)
    - `resolved → closed`
    - `in_progress → open` (deprioritise)
    - `resolved → in_progress` (reopen)

    Anything not listed above — including skipping straight from `open` to `resolved`
    or `closed`, or moving out of `closed` at all — returns `409`. A move into
    `resolved` that *is* legal still returns `409` if the ticket has no comment on it
    yet — that check runs independently of the transition table.

---

## Files used in Lab

**Learner starter files (you implement these):**

- `tests/conftest.py`
- `tests/factories.py`
- `tests/test_smoke.py`
- `tests/test_workflow.py`
- `tests/test_migration.py`
---

## Task 1: Build the test harness

**Target files:**
`tests/conftest.py`
`tests/test_smoke.py`

### Goal

Build the fixtures every later task in this lab depends on, and prove them with one
smoke test:

- A `client` fixture for making requests against the running API.
- `user_headers` and `admin_headers` fixtures that authenticate once as each role and
  hand back a reusable auth header. You need admin now, not just later: viewing
  another user's ticket comments and creating categories both require it.
- A cleanup-tracking fixture that deletes any tickets a test created, even if the
  test itself failed.
- A smoke test that creates one ticket and proves it exists.

### How to approach it

Ask Copilot to scaffold each fixture in turn, then wire them together in
`conftest.py`. Auth is a two-step job: log in once, then reuse the resulting header
everywhere the API expects one — don't repeat the login call in every test. To
confirm the ticket exists, look it up with `GET /tickets/search?q=<your unique
marker>` rather than paging through the full ticket list.

### Things to know

- Make sure your cleanup fixture runs on failure, not just on success. That's the
  entire reason to use a `yield`-based fixture instead of a plain helper function —
  test it by making an assertion fail on purpose once and confirming the ticket still
  gets deleted afterwards.

### Run

```bash
pytest tests/test_smoke.py -v
```

### Done when

Your smoke test passes, login/cleanup logic lives in fixtures rather than the test
body, and running `pytest tests/test_smoke.py -v` twice in a row leaves no extra
tickets behind.

---

## Task 2: Dependency-aware data factories

**Target files:**
`tests/factories.py`
`tests/test_smoke.py` (extend)

### Goal

Tickets now have real rules attached to them (a category that must exist, a status
workflow), so your test data needs to satisfy those rules, not just look realistic.
You'll need to write a few methods to get there:

- `make_ticket()` and `make_comment()` factories in `tests/factories.py`.
- A `ticket_in_status()` scenario builder that can put a fresh ticket into any of the
  four workflow statuses.
- Your Task 1 smoke test, updated to actually use these — this is what proves they
  work, rather than taking them on faith until Task 3.

### How to approach it

- `make_ticket()` — builds a ticket payload. A valid ticket now needs a real
  category, so this can't just be Faker data: it has to fetch the category list from
  the API and pick one, plus tag the title with a unique marker so tests can find
  their own rows later. Still allow overrides for whatever a test wants to control.
- `make_comment()` — the same idea, simpler: just a comment body.
- `ticket_in_status()` — the real challenge. Given a target status, it creates a
  ticket with `make_ticket()`, registers it with your Task 1 cleanup fixture, and
  walks it through the workflow (create → transition → comment → transition) until it
  lands there, instead of every test doing that walk by hand. This is what every
  later task leans on to arrange "a ticket already in some state" in one call.
- Once those work, go back to `test_smoke.py`: swap the hand-built payload for
  `make_ticket()`, and add a test that calls `ticket_in_status()` once per status and
  checks the ticket actually landed there.

### Run

```bash
pytest tests/test_smoke.py -v
```

### Done when

Your smoke test creates its ticket through `make_ticket()` instead of a hand-built
payload, and a new test proves `ticket_in_status()` can reach all four statuses.

---

## Task 3: Parametrise the rulebook

**Target file:**
`tests/test_workflow.py`

You've now got a harness that can log in and clean up after itself (Task 1), and
factories that can hand you a ticket in any state with one call (Task 2). Time to put
that to work: instead of writing one-off tests by hand, use it to check every rule
the API enforces, systematically.

### Goal

Replace hand-picked examples with three parametrised tests that pin down the API's
actual business rules:

- `test_status_transitions` — one parametrised test covering every status
  transition, legal and illegal, with the status code each one should return.
- `test_resolve_without_comment_is_rejected` and `test_resolve_with_comment_succeeds`
  — two tests proving the resolution-note rule.
- `test_ticket_validation` — one parametrised test covering which severities and
  `category_id` values the API accepts vs rejects.

### How to approach it

- **Transition matrix** — for each `(from_status, to_status)` pair you want to cover,
  use `ticket_in_status()` to get a ticket into `from_status`, attempt the transition,
  and assert the code you expect: `200` for a legal move, `409` for anything not in
  the workflow note above. Use that note as your source of truth, not a guess.
- **Resolution-note rule** — two tests, same setup: get a ticket to `in_progress`,
  try to resolve it with no comments first (expect `409`), then repeat after adding a
  comment (expect `200`).
- **Validation table** — build payloads with `make_ticket()` and override one field
  at a time: a few valid severities (expect `201`), a few invalid ones (expect
  `400`), and a `category_id` that doesn't exist (expect `404`).

Ask Copilot to draft each parameter table, but check its answers against the real
rules before trusting them — a guessed transition table isn't the same as a verified
one.

### Things to know

- `closed` is a dead end — every transition *out of* `closed` should expect `409`.
- A legal transition into `resolved` still isn't enough on its own: it also needs a
  comment on the ticket first, or it's a `409` too.

### Run

```bash
pytest tests/test_workflow.py -v
```

### Done when

Your transition matrix, resolution-note tests, and validation table all pass, and each
uses `@pytest.mark.parametrize` rather than repeating near-identical test bodies.

---

## Congratulations!

!!! success
    You've completed the lab — you built a test harness from scratch, taught it to
    generate data for a stateful, relational API, turned its business rules into
    parametrised tests, and rehearsed a legacy migration against a real, messy export.
    That's the full toolkit a QA engineer needs when a legacy system meets its modern
    replacement. Nice work!
