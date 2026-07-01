# Lab 4 Load & Performance Testing with JMeter

## Overview

You will write JMeter load tests for the **TaskDesk API**, a REST service that manages
support tickets, running locally on your machine. The API behaves correctly — all endpoints
return the right data and the right status codes. Your job is to find out whether it
behaves *well under load*.

**Estimated time:** 60 minutes

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

---

## Setup

### 1. Enter the project and create a virtual environment

```bash
cd src/ticket-api

python3 -m venv .venv
source .venv/bin/activate     # macOS / Linux
# .venv\Scripts\activate      # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up the database


```bash
# creates the database and populates it with test accounts and tickets
python seed.py   
```

### 4. Start the API

In a separate terminal:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

!!! note
      The interactive docs are at **http://localhost:8080/docs** — use them to explore the
      endpoints before writing tests.

Verify it's running:

```bash
curl http://localhost:8080/health
```

!!! note "Accounts"

    | Username | Password | Role |
    |----------|----------|------|
    | `user` | `user` | Regular user |
    | `admin` | `admin` | Admin |

---

## Task 1: Smoke Test

Before anyone runs a full load test against the TaskDesk API, you need a lightweight sanity check — a single simulated user hitting the core endpoints repeatedly to confirm the application behaves correctly and consistently before scaling up.

!!! note "Before you start"
    You'll need JMeter installed to build and run anything below. If you're not sure how to get it on your machine, that's a good first question to put to Copilot.

    ??? tip " if Copilot doesn't get you there"
        ```bash
        # macOS
        brew install jmeter
        ```
        Or download it from [jmeter.apache.org/download_jmeter.cgi](https://jmeter.apache.org/download_jmeter.cgi) (requires Java 8+).

### Requirements

Build a test plan that:

1. **Simulates a single user** running many iterations back-to-back — enough repetitions that a one-off fluke wouldn't be mistaken for a real problem.

2. **Authenticates once and reuses the session** for every subsequent request in that user's iterations — think about where the credentials need to live so they don't have to be re-entered on every loop.

3. **Exercises these endpoints, per iteration:**
   - `GET /health`
   - `GET /tickets/`

4. **Confirms the application is reachable and responding correctly**, not just that requests were sent — think about what you need to check in each response to be confident the test actually validated something.

5. **Captures results in a form you can review afterward** — both a detailed per-request view (for debugging failures) and a statistical summary (for spotting patterns across iterations).

### Constraints

- Do not hardcode the host/port into every individual request — use a config element shared across the whole test.
- Your test must run cleanly in **non-GUI (headless) mode** — anything that only works in GUI mode is not a valid solution.
- This is a smoke test, not a load test — resist the urge to add concurrency here. Task 2 will scale this up.

### Run it headless

```
jmeter -n -t <your-file>.jmx -l results.jtl
```

### Deliverables

1. Your `.jmx` file
2. `results.jtl` output from the run
3. The HTML report generated from your results
4. All requests must pass — a 0% error rate in the Aggregate Report

!!! note "Running your test plan"
    Run it headless from the command line:

    ```bash
    jmeter -n -t smoke.jmx -l results_smoke.jtl
    ```

    Then turn those results into a browsable HTML report:

    ```bash
    jmeter -g results_smoke.jtl -o report_smoke
    ```

    Open `report_smoke/index.html` in your browser to see the dashboard, or open
    `results_smoke.jtl` directly in JMeter's **Aggregate Report** / **View Results Tree**
    listeners for the raw per-sample data.

    ??? tip "Prefer a GUI?"
        You can also open JMeter's desktop UI, import the `.jmx` file, and run it from
        there instead of headless. See the official
        [Building a Test Plan](https://jmeter.apache.org/usermanual/get-started.html)
        guide for how to open and run a plan in the GUI.

---

## Task 2: Scale-Up Load Test

Your Task 1 test proved the login flow works for a single user. Now you need to find out how the API behaves under realistic concurrent load — and whether the search endpoint holds up to an SLA.

### Requirements

Build on your Task 1 test plan (or start fresh if you prefer) to produce a test that:

1. **Simulates 50 concurrent users**, ramped up gradually rather than launched all at once — think about what ramp-up period gives you a realistic climb to full load without spiking the server instantly.

2. **Authenticates once per user session** and reuses that session's credentials for all subsequent requests — you already solved this in Task 1; figure out how to make it work per-thread at scale rather than per-request.

3. **Exercises both of these endpoints, per user, per loop:** `GET /tickets/` and `GET /tickets/search?q=login`

4. **Produces enough samples to be statistically meaningful.** A single pass per user won't cut it — decide how many iterations you need, and be ready to justify your choice.

5. **Flags SLA violations automatically.** The search endpoint has a target response time. Add an assertion that fails any request exceeding **1000 ms**, and think about which endpoint(s) actually need it.

6. **Captures results in a form you can analyze after the run** — not just a live view. Choose a listener suited to statistical summaries (avg, median, 90th percentile, error %) rather than per-request inspection.

### Constraints

- Do not hardcode the host/port into every individual request — use a config element shared across the whole test.
- Your test must run cleanly in **non-GUI (headless) mode** — anything that only works in GUI mode is not a valid solution.
- If you leave any listener enabled that stores full response data for every sample, be prepared to explain why that's a problem at 50-user scale.

### Run it headless

```
jmeter -n -t <your-file>.jmx -l results.jtl
```

### Deliverables

1. Your `.jmx` file
2. `results.jtl` output from the run
3. The HTML report generated from your results

??? note "Once you've done that"
    Got an endpoint failing its Duration Assertion, or behaving much worse than the other
    as concurrency rises?

    1. Find its route in the API source and investigate why it holds up for one user
       but not fifty. You don't need to fix it — just identify the likely cause.
    2. Note what you found — this is what you'll summarise in Task 3.
    3. If you want to confirm your suspicion, you can try a fix locally and re-run into
       a new file to compare, but this is optional and not required for the lab

---

## Task 3: Findings Report

The development team wants a short write-up of what your testing found — whether everything held up under load, or whether something needs attention before this ships to production.


### Requirements

Write a short report that answers:

1. **What did your Aggregate Report show?** Include the key metrics for each endpoint you tested, from both your smoke test and your load test.

2. **Did anything stand out?** If any endpoint's behavior changed between the two tests, investigate and summarise what you found.

3. **Did you make any changes?** If so, describe what you changed and compare the before/after Aggregate Reports for the affected endpoint.

4. **Why might a single-user test and a 50-user test produce different results?** What is fundamentally different about the two scenarios?

5. **What would you tell the development team?** Summarise your findings, including anything they should know before shipping.


!!! tip "Use GitHub Copilot to write your report"
    Draft your findings report with GitHub Copilot rather than writing it from scratch.
    Paste in your Aggregate Report numbers (before/after, if you have them) and the notes
    from your investigation, then ask Copilot to turn them into a short Markdown report
    that answers the five questions above.

### Deliverables

1. Your report `report.md`

## Congratulations!

!!! success
    You've completed the lab — you built a smoke test, scaled it into a load test,
    investigated a real concurrency issue, and reported your findings like a QA
    engineer would in the field. Nice work!

