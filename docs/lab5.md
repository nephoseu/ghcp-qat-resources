# Lab 5 Generating Test Data & Building a Test Harness with GitHub Copilot

## Overview

In this lab, you will modernise testing around a legacy-to-modern API migration by building a
small pytest harness and using GitHub Copilot to generate test data for parametrised tests.

You will work against **TaskDesk API** (`ticket_api`), which already has seed data but no
automated tests.

**App under test:** TaskDesk API (FastAPI)  
**Estimated time:** 60–90 minutes

!!! tip "Download the app first"
    Lab 5 uses **TaskDesk API (FastAPI)**. Download and unzip it before following the setup steps below.

    [Download taskdesk-api.zip](https://github.com/nephoseu/ghcp-qat-resources/releases/latest/download/taskdesk-api.zip){ .md-button }

---

## Setup

### 1. Enter the API project and create a virtual environment

```bash
cd ghcp-qat-resources/src/ticket-api

python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install pytest httpx faker
```

### 3. Seed data and start the API

```bash
python seed.py
uvicorn app.main:app --host 0.0.0.0 --port 8081
```

In a second terminal, verify:

```bash
curl http://localhost:8081/health
```

You should get `{"status":"ok"}`.

**Demo accounts:**

| Username | Password | Role |
|----------|----------|------|
| `user` | `user` | Regular user |
| `admin` | `admin` | Admin |

### 4. Use pytest from `ticket_api/`

Run pytest from this folder so it uses `ticket_api/pytest.ini` and does not inherit the
repo-root Django pytest config.

---

## API notes for this lab

| Endpoint | Notes |
|----------|-------|
| `POST /auth/login` | Form-encoded `username`, `password`; returns token |
| `POST /tickets/` | Requires Bearer token; `severity` defaults to `medium`; invalid severity returns `400` |
| `GET /tickets/` | Lists tickets for the authenticated user |
| `GET /tickets/search?q=` | Case-insensitive title substring search |

---

## File separation (starter vs solution)

**Learner starter files (you implement these):**
- `tests/conftest.py`
- `tests/factories.py`
- `tests/test_smoke.py`
- `tests/test_severity.py`
- `tests/test_search.py`

---

## Task 1 — Build the test harness (fixtures)

**Target files:**  
`tests/conftest.py`  
`tests/test_smoke.py`

### Goal

Create a reusable pytest harness so tests can call the live API without copy-pasting login
and setup code.

### How to approach it

1. Ask Copilot to scaffold a `client` fixture using `httpx` with a base URL pointing to the
   running API.
2. Add an `auth_headers` fixture that logs in as `user/user` and returns
   `{"Authorization": "Bearer <token>"}`.
3. Write a smoke test that creates one ticket and verifies it appears in `GET /tickets/`.

### Things to know

- `POST /auth/login` expects **form data** (`data=...`), not JSON.
- Keep this as a harness foundation: login once in a fixture, reuse everywhere.
- Since the database is shared and pre-seeded, avoid brittle assertions on total ticket count.

### Run

```bash
pytest tests/test_smoke.py -v
```

### Done when

Your smoke test passes and does not duplicate login logic in test bodies.  
Reference answer key: `tests/solutions/test_smoke.py` + `tests/solutions/conftest.py`.

---

## Task 2 — Generate test data with a factory (Faker)

**Target files:**  
`tests/factories.py`  
`tests/conftest.py` (extend with `ticket_factory` fixture)

### Goal

Use Copilot to generate realistic, varied ticket payloads so test data is reusable and
isolated.

### How to approach it

1. In `tests/factories.py`, create `make_ticket(**overrides)`.
2. Use Faker for title/description and random valid severity (`critical/high/medium/low`).
3. Add a unique marker in generated titles (for example a short UUID fragment) so tests can
   identify their own rows in a shared DB.
4. Add `ticket_factory` fixture in `conftest.py` that creates `N` tickets via API and returns
   the created records.

### Things to know

- Keep defaults realistic; allow overrides like `make_ticket(severity="critical")`.
- The unique marker is part of your isolation strategy.
- Builder/factory pattern keeps test logic clean and focused.

### Run

```bash
pytest tests/test_smoke.py -v
```

### Done when

At least one test uses `make_ticket(...)` instead of hard-coded payload literals.  
Reference answer key: `tests/solutions/factories.py` + updated `tests/solutions/conftest.py`.

---

## Task 3 — Parametrise tests with generated data

**Target files:**  
`tests/test_severity.py`  
`tests/test_search.py`

### Goal

Separate test logic from test data by combining generated payloads with
`@pytest.mark.parametrize`.

### How to approach it

1. **Severity tests**
   - Parametrise valid severities (`critical`, `high`, `medium`, `low`) and assert `201`.
   - Parametrise invalid severities (`""`, `"urgent"`, `"HIGH"`) and assert `400`.
2. **Search tests**
   - Use the factory to create tickets carrying a known unique marker in the title.
   - Parametrise `(query, expected_match)` pairs and assert marker-tagged tickets are
     returned only when expected.
3. Ask Copilot to propose the parameter table, then review and tighten edge cases.

### Things to know

- Search is case-insensitive substring match.
- Parametrisation should reduce duplicate test code to a single test body per behavior.
- Keep assertions focused on tickets created by your test marker.

### Run

```bash
pytest tests/test_severity.py tests/test_search.py -v
```

### Done when

Both files pass and each uses `@pytest.mark.parametrize` with generated test data.  
Reference answer key: `tests/solutions/test_severity.py` and `tests/solutions/test_search.py`.

---

## Stretch (optional)

Try boundary data in your factory and parameters:
- very long titles
- empty strings
- unicode text

Keep this as exploratory work; no extra deliverable file is required.

---

## Quick reference

### Pytest run commands

```bash
# Run only solution key (instructor verification)
pytest tests/solutions -v

# Run individual task files
pytest tests/test_smoke.py -v
pytest tests/test_severity.py -v
pytest tests/test_search.py -v
```

### Parametrize snippet

```python
@pytest.mark.parametrize("severity, expected", [
    ("critical", 201),
    ("urgent", 400),
])
def test_create_ticket_severity(...):
    ...
```

### Faker + factory snippet

```python
payload = make_ticket(severity="critical")
```

### Login + Bearer flow

```text
POST /auth/login  (form: username, password) -> access_token
Authorization: Bearer <access_token>
```
