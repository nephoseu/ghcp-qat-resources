# Lab 4 Load & Performance Testing with JMeter

## Overview

You will write JMeter load tests for the **TaskDesk API**, a REST service that manages
support tickets. The API behaves correctly — all endpoints return the right data and the
right status codes. Your job is to find out whether it behaves *well under load*.

**API under test:** TaskDesk API (FastAPI)  
**Estimated time:** 60–90 minutes

!!! tip "Download the app first"
    Lab 4 uses **TaskDesk API (FastAPI)**. Download and unzip it before following the setup steps below.

    [Download taskdesk-api.zip](https://github.com/nephoseu/ghcp-qat-resources/releases/latest/download/taskdesk-api.zip){ .md-button }

---

## Background

Functional tests tell you whether an endpoint returns the correct response. They say nothing
about what happens when many users hit that endpoint at the same time.

Load testing sends concurrent requests and measures how response time and throughput change
as the number of users increases. A single slow request might go unnoticed. A hundred slow
requests happening simultaneously can expose something very different.

In this lab you will design load tests that reveal the performance characteristics of each
endpoint. Some endpoints will behave well under load. At least one will not. It is your job
to find it and explain why.

---

## JMeter building blocks

| Element | What it does |
|---------|--------------|
| **Thread Group** | Defines the load profile — how many virtual users, how fast to ramp them up, how long to run |
| **HTTP Request sampler** | Sends a single HTTP request |
| **HTTP Header Manager** | Adds request headers (scoped to the element it is attached to, or everything below it) |
| **JSON Extractor** | Reads a value from a JSON response body and saves it to a variable |
| **Duration Assertion** | Marks a sample as failed if it takes longer than a given threshold |
| **Aggregate Report** | Shows per-sampler statistics: avg, p90, p95, p99, throughput, error % |
| **View Results Tree** | Shows raw request and response for each sample — useful for debugging |

> Build your test plan in the JMeter GUI. Run load tests with the headless CLI
> (`jmeter -n -t plan.jmx -l results.jtl`) — the GUI consumes CPU and skews results.

---

## Setup

### 1. Install JMeter

```bash
# macOS
brew install jmeter

# Or download from https://jmeter.apache.org/download_jmeter.cgi  (requires Java 8+)
```

Verify: `jmeter --version`

### 2. Install the API dependencies

```bash
cd ghcp-qat-resources/src/ticket-api

python3 -m venv .venv
source .venv/bin/activate     # macOS / Linux
# .venv\Scripts\activate      # Windows

pip install -r requirements.txt
python seed.py
```

`seed.py` creates the database and populates it with test accounts and tickets.

### 3. Start the API

In a separate terminal:

```bash
uvicorn main:app --host 0.0.0.0 --port 8081
```

Verify it's running:

```bash
curl http://localhost:8081/health
```

The interactive docs are at **http://localhost:8081/docs** — use them to explore the
endpoints before writing tests.

**Accounts:**

| Username | Password | Role |
|----------|----------|------|
| `user` | `user` | Regular user |
| `admin` | `admin` | Admin |

---

## API Reference

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Liveness check |
| POST | `/auth/login` | — | Form body `username` + `password` → `{"access_token": "..."}` |
| GET | `/tickets/` | Bearer | List tickets for the authenticated user |
| GET | `/tickets/search?q=` | Bearer | Search tickets by title |
| POST | `/tickets/` | Bearer | Create a ticket |
| DELETE | `/tickets/{id}` | Bearer | Delete own ticket |

All protected endpoints require an `Authorization: Bearer <token>` header. Obtain the token
from `/auth/login`.

---

## Task 1 — Verify the API with a single user

**Deliverable:** `smoke.jmx`

Design a JMeter test plan that logs in as `user`, then exercises the main read endpoints
(`/health`, `/tickets/`, `/tickets/search`). Run it with a single virtual user.

Your test plan must:
- Obtain a token from `/auth/login` and reuse it for subsequent requests.
- Send at least 20 iterations.
- Confirm all responses return HTTP 200.

Record the response times you see. This is your baseline — the numbers a single user
experiences with no competition.

---

## Task 2 — Load test

**Deliverable:** `load_test.jmx`

Now scale up. Design a test plan that ramps to at least 50 concurrent virtual users and
runs each endpoint long enough to produce stable statistics.

Your test plan must:
- Include both `GET /tickets/` and `GET /tickets/search`.
- Add a **Duration Assertion** on each endpoint with a threshold you consider reasonable
  (justify your choice in your report).
- Capture results in an **Aggregate Report**.

Run the test headless:

```bash
jmeter -n -t load_test.jmx -l results.jtl
```

Examine the Aggregate Report. Compare each endpoint across: average, p90, p95, p99,
throughput, and error %.

---

## Task 3 — Findings report

Write a short report (≤ 300 words) that answers:

1. **What do the numbers show?** Include the key metrics from your Aggregate Report for
   each endpoint you tested.

2. **Is there an endpoint that behaves differently under load?** If so, describe how its
   behaviour changes as concurrency increases.

3. **Why do you think the single-user test did not reveal this?** What is fundamentally
   different about the two scenarios?

4. **What would you tell the development team?** Describe the symptom and your hypothesis
   about the underlying cause.

Attach both `.jmx` files to your submission.

---

## Quick reference

### JMeter GUI

| What you need | How to add it |
|---------------|---------------|
| Virtual users / load profile | Right-click Test Plan → Add → Threads → Thread Group |
| HTTP request | Right-click Thread Group → Add → Sampler → HTTP Request |
| Request headers | Right-click Thread Group (or Sampler) → Add → Config Element → HTTP Header Manager |
| Extract value from JSON response | Right-click a Sampler → Add → Post Processors → JSON Extractor |
| Assert response time | Right-click a Sampler → Add → Assertions → Duration Assertion |
| See raw results | Right-click Thread Group → Add → Listener → View Results Tree |
| See aggregated stats | Right-click Thread Group → Add → Listener → Aggregate Report |

### Headless run

```bash
jmeter -n -t load_test.jmx -l results.jtl

# Optional HTML report
jmeter -g results.jtl -o report/
open report/index.html
```

### Bearer token flow

```
POST /auth/login   ←  form params: username, password
                   →  {"access_token": "eyJ..."}
                                         ↓
                       JSON Extractor saves it → ${TOKEN}
                                         ↓
                       HTTP Header Manager sends:
                       Authorization: Bearer ${TOKEN}
```
