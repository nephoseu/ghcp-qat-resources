# Downloads

Download the application you need for your lab. Each ZIP is self-contained — unzip it and follow the setup steps inside the lab.

---

## TaskDesk — Django app (Lab 3)

The Django ticket management app that serves as the test target for Lab 1 (Selenium to Playwright migration).

**Port:** 8080  
**Credentials:** `user / user` and `admin / admin`

[Download taskdesk-django.zip](https://github.com/nephoseu/ghcp-qat-resources/releases/latest/download/taskdesk-django.zip){ .md-button .md-button--primary }

### What's included

- `manage.py`, `ticketapp/`, `tickets/` — Django project
- `requirements.txt`
- `tests/e2e.py`, `tests/e2e_advanced.py` — Selenium baselines to migrate
- `tests/conftest.py` — pytest fixtures

---

## TaskDesk API — FastAPI app (Labs 4 & 5)

The FastAPI REST service used for load testing (Lab 2) and test harness construction (Lab 3).

**Port:** 8081  
**Credentials:** `user / user` and `admin / admin`

[Download taskdesk-api.zip](https://github.com/nephoseu/ghcp-qat-resources/releases/latest/download/taskdesk-api.zip){ .md-button .md-button--primary }

### What's included

- `app/` — FastAPI application
- `seed.py` — creates the database and demo accounts
- `requirements.txt`
- `tests/` — starter files for Lab 3

---

!!! note "Version"
    These ZIPs are built from the latest tagged release of this repository.
    To browse all past releases, visit the [releases page](https://github.com/nephoseu/ghcp-qat-resources/releases).
