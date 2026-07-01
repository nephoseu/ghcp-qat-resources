# Lab 3 Selenium to Playwright Migration with GitHub Copilot

## Overview

You will migrate an existing Selenium test suite to Playwright in three stages: a straightforward conversion, a set of patterns where naive migration breaks, and finally writing a brand-new test from scratch. GitHub Copilot is your assistant throughout — but you will need to know enough to steer it and fix what it gets wrong.

**Estimated time:** 60 minutes

!!! tip "Download the app first"
    Lab 3 uses **TaskDesk (Django)**. Download and unzip it before following the setup steps below.

    [Download taskdesk-django.zip](https://github.com/nephoseu/ghcp-qat-resources/releases/latest/download/taskdesk-django.zip){ .md-button }

---

## Setup

### 1. Enter the project and create a virtual environment

```bash
cd src/ticket-app-django

python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up the database

```bash
python manage.py migrate
python manage.py seed             # creates demo accounts and sample tickets
python manage.py runserver 0.0.0.0:8080
```

### 4. Start the Django App
```bash
python manage.py runserver 0.0.0.0:8080
```

Open `http://localhost:8080` in your browser. You should see the TaskDesk login page.

!!! note "Demo accounts"

    | Username | Password | Role |
    |----------|----------|------|
    | `user` | `user` | Regular user |
    | `admin` | `admin` | Admin |

### 5. Verify the existing Selenium suite runs

In a second terminal (with the venv activated):

```bash
pytest tests/e2e.py -v
```

All five tests should pass before you start.

---

## Task 1: Basic Migration to Playwright with Copilot


### Goal

Use GitHub Copilot to convert the existing Selenium tests in `tests/e2e.py` into Playwright.

That file covers four flows:

- `test_auth_flow` — login as a regular user, check the welcome label, then log out.
- `test_invalid_login_shows_error` — wrong password shows the login error message.
- `test_user_submit_ticket` — fill in the ticket form and confirm the new ticket shows up in the table.
- `test_admin_login_and_close_ticket` — admin logs in, closes a user's ticket, status badge updates.

!!! note "Before you start"
    You'll need Playwright and its pytest plugin installed in your venv before any of this will run. If you're not sure what to install or how, that's a good first question to put to Copilot.

### How to approach it

1. Create a new file, e.g. `tests/e2e_basic_migration.py`, and open it side by side with `tests/e2e.py`.
2. Go test by test: put the Selenium version in view, then let Copilot suggest a Playwright equivalent — either via inline suggestions as you type the new function, or by asking Copilot Chat to convert the selected test.
3. Accept what makes sense, correct what does not.
4. Pay attention to what Copilot removes vs. what it keeps — it will sometimes drop waits or assertions that were load-bearing in the Selenium version.
5. Run your converted tests as you go:

```bash
pytest tests/e2e_basic_migration.py
```

!!! note
    Add `--headed` to watch the browser while a test runs.

---

## Task 2: Advanced Migration to Playwright with Copilot


### Goal

The six Selenium tests in `tests/e2e_advanced.py` each cover a browser pattern that does not translate directly to Playwright. Use Copilot to convert them, then fix what it gets wrong — it will get some of these partially right and others completely wrong.

Work through the tests in order. For each one, read what the test does, then write the Playwright version.

### How to approach it

1. Create a new file, e.g. `tests/e2e_advanced_migration.py`, and open it side by side with `tests/e2e_advanced.py`.
2. Convert one test at a time — do not skip ahead, since later tests assume you already know the pattern from an earlier one.
3. Run each test as soon as you convert it:

```bash
pytest tests/e2e_advanced_migration.py -v
```

!!! note
    Add `--headed` to watch the browser while a test runs.

---

### Test 1: Confirming a delete

Found in `tests/e2e_advanced.py` as `test_confirm_delete_dialog`.

**What it does:** Clicks the red **Delete!** button on a ticket row, which triggers a native browser `confirm()` dialog, and verifies the ticket is removed once the dialog is accepted.

---

### Test 2: Ticket details in an iframe

Found in `tests/e2e_advanced.py` as `test_ticket_detail_in_iframe`.

**What it does:** Clicks the **View** button on a ticket row, which loads the ticket detail page inside a `#ticket-detail-frame` iframe embedded on the same page, and checks the detail content.

---

### Test 3: Opening a ticket in a new tab

Found in `tests/e2e_advanced.py` as `test_open_ticket_in_new_tab`.

**What it does:** Clicks the **↗** link, which opens the ticket detail page in a new browser tab (`target="_blank"`), and checks the content of that new tab.

---

### Test 4: A toast that dismisses itself

Found in `tests/e2e_advanced.py` as `test_toast_auto_dismiss`.

**What it does:** Submits a ticket and checks that a toast notification appears at the bottom-right of the screen, then disappears automatically after 3 seconds.

---

### Test 5: A button inside shadow DOM

Found in `tests/e2e_advanced.py` as `test_shadow_dom_copy_widget`.

**What it does:** Clicks the **Copy ID** button rendered inside a shadow DOM web component (`<copy-id-widget id="copy-widget-{id}">`) on a ticket row, and checks that a **Copied!** message appears.

---

### Test 6: Dragging a card between kanban columns

Found in `tests/e2e_advanced.py` as `test_drag_drop_kanban_close`.

**What it does:** On the admin dashboard's two-column kanban board, drags a card from the **Open** column (`#col-open`) to the **Closed** column (`#col-closed`) and checks that the ticket is closed.

---

## Task 3: Write a Playwirght Test from Scratch with Copilot


### Goal

Write a Playwright tests for the live search filter on the user dashboard — entirely from scratch, without a Selenium version to convert.

### What the feature does

Typing in `#ticket-search-input` filters the tickets table live:

- After a 300 ms debounce, the page calls `GET /tickets/search/`, which runs a case-insensitive `icontains` query against the title in the database and returns the matching ticket IDs.
- Rows whose ID isn't in the response are hidden.
- If nothing matches, `#search-empty` appears.
- Clearing the input restores all rows and hides `#search-empty`.

### Write two tests

Cover the positive and negative cases separately, so a failure tells you exactly which behavior broke.

**`test_search_returns_matching_results`** — with a couple of tickets of different titles, search for one and confirm it's the only row showing.

**`test_search_shows_empty_state_when_no_match`** — search for something that matches nothing and confirm `#search-empty` shows up instead.

### Run your tests

```bash
pytest tests/e2e_advanced_migration.py -v
```

!!! note
    Add `--headed` to watch the browser while a test runs.
---

## Congratulations!

!!! success
        You've completed Lab 3 — you migrated Selenium tests to Playwright, tackled the tricky patterns, and wrote a test from scratch.
