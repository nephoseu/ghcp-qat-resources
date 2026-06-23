# TaskDesk

A simple ticket management web app built with **Django 5.2** and **SQLite**. Designed as a test target for Selenium automation — every interactive element has a stable `id` attribute.

## What it does

- **Regular users** can sign in, submit support tickets, and delete their own tickets.
- **Admins** see all tickets from all users and can close them. Admins cannot submit tickets.
- Two roles are fully separated — each lands on a different page after login.

### Seeded accounts

| Username | Password | Role  |
|----------|----------|-------|
| `user`   | `user`   | User  |
| `admin`  | `admin`  | Admin |

Accounts are created automatically on first `migrate`.

---

## Project structure

```
ghcp-qat-resources/
├── manage.py
├── requirements.txt
├── ticketapp/          # Django project config (settings, urls, wsgi)
├── tickets/            # Main Django app
│   ├── api.py          # Business logic (create, delete, close tickets)
│   ├── views.py        # HTTP layer (renders templates, handles redirects)
│   ├── models.py       # Ticket model
│   ├── forms.py        # LoginForm, TicketForm
│   ├── urls.py         # URL routes
│   └── templates/
│       └── tickets/
│           ├── login.html
│           ├── dashboard.html
│           ├── admin_dashboard.html
│           └── detail.html          # Ticket detail page (iframe / new-tab target)
└── tests/
    ├── e2e.py                # Simple Selenium tests (baseline)
    ├── e2e_advanced.py       # Advanced Selenium tests — convert these to Playwright
    ├── conftest.py
    └── solutions/
        └── solution_advanced_playwright.py   # Instructor answer keys (not auto-collected)
```

---

## Running the app

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd ghcp-qat-resources
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py migrate
```

This creates `db.sqlite3` and seeds the `user` and `admin` accounts.

### 5. Start the development server

```bash
python manage.py runserver 0.0.0.0:8080
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

---

## Running the tests

### Baseline Selenium tests

```bash
pytest tests/e2e.py
pytest tests/e2e.py --headed     # visible browser
```

### Advanced Selenium tests (migration lab)

```bash
pytest tests/e2e_advanced.py
pytest tests/e2e_advanced.py --headed
```

### Instructor Playwright answer keys (not run by default)

Install playwright first:

```bash
pip install playwright==1.60.0 pytest-playwright==0.8.0
playwright install chromium
```

Then run:

```bash
pytest tests/solutions/solution_advanced_playwright.py
pytest tests/solutions/solution_advanced_playwright.py --headed --slowmo 600
```

### Run everything (baseline + advanced Selenium)

```bash
pytest tests/
```

> `tests/solutions/` is **not** auto-collected — the solution file does not match the
> `test_*.py` or `e2e*.py` patterns in `pytest.ini`.

---

## URL reference

| URL | Method | Description |
|-----|--------|-------------|
| `/` | GET, POST | Login page |
| `/logout/` | POST | Sign out |
| `/dashboard/` | GET, POST | User dashboard — list and submit tickets |
| `/tickets/<id>/delete/` | POST | Delete a ticket (owner only) |
| `/admin-dashboard/` | GET | Admin view — all tickets + kanban board |
| `/tickets/<id>/close/` | POST | Close a ticket (admin only) |
| `/tickets/<id>/detail/` | GET | Ticket detail page (for iframe / new tab) |

---

## Selenium element IDs

All stable `id` attributes for test selectors:

### Login page

| Element | ID |
|---------|----|
| Username input | `username-input` |
| Password input | `password-input` |
| Login button | `login-button` |
| Login error message | `login-error` |

### User dashboard

| Element | ID |
|---------|----|
| Welcome label | `welcome-label` |
| Logout button | `logout-button` |
| Ticket title input | `ticket-title-input` |
| Ticket description input | `ticket-description-input` |
| Severity select | `ticket-severity-select` |
| Submit ticket button | `submit-ticket-button` |
| Tickets table | `tickets-table` |
| Delete button (per row, no dialog) | `delete-ticket-{id}` |
| Empty state message | `empty-state` |
| **Toast notification** | `toast` |
| **Search input** | `ticket-search-input` |
| **No-match message** | `search-empty` |
| **Confirm-delete button (per row)** | `confirm-delete-{id}` |
| **View-in-iframe button (per row)** | `view-ticket-{id}` |
| **Iframe container** | `ticket-detail-frame` |
| **Open-in-new-tab link (per row)** | `open-tab-{id}` |
| **Shadow-DOM copy-ID widget (per row)** | `copy-widget-{id}` |
| Shadow root: copy button | `.copy-btn` (inside `#copy-widget-{id}` shadow root) |
| Shadow root: copied message | `.copied-msg` (inside `#copy-widget-{id}` shadow root) |

### Admin dashboard

| Element | ID |
|---------|----|
| Admin welcome label | `admin-welcome-label` |
| Logout button | `logout-button` |
| Tickets table | `tickets-table` |
| Close button (per row) | `close-ticket-{id}` |
| Ticket status badge (per row) | `ticket-status-{id}` |
| Empty state | `empty-state` |
| **Kanban open column** | `col-open` |
| **Kanban closed column** | `col-closed` |
| **Kanban card (per ticket)** | `card-{id}` |

### Ticket detail page (`/tickets/<id>/detail/`)

| Element | ID |
|---------|----|
| Title | `detail-title` |
| Description | `detail-description` |
| Severity badge | `detail-severity` |
| Status badge | `detail-status` |
| Close button | `close-detail-button` |

---

## Advanced migration lab

`tests/e2e_advanced.py` contains **six Selenium tests** that exercise patterns where a
naive line-by-line conversion to Playwright breaks. Convert each one to Playwright.

| Test | Feature | What breaks in a naive conversion |
|------|---------|-----------------------------------|
| `test_confirm_delete_dialog` | JS `confirm()` dialog | Ordering — PW needs `page.on("dialog")` **before** the click |
| `test_ticket_detail_in_iframe` | Iframe content | `switch_to.frame` vs `frame_locator()` — different paradigm |
| `test_open_ticket_in_new_tab` | `target=_blank` link | `window_handles` vs `context.expect_page()` |
| `test_toast_auto_dismiss` | Auto-dismissing toast | Two separate `WebDriverWait` calls vs two `expect()` assertions |
| `test_shadow_dom_copy_widget` | Shadow DOM widget | `.shadow_root` traversal vs automatic CSS piercing |
| `test_drag_drop_kanban_close` | Kanban drag-and-drop | `ActionChains` mouse simulation vs `drag_to()` |

### Exercise: write the seventh test yourself

The live search filter (`#ticket-search-input`) has **no Selenium test provided**.
Write the Playwright test from scratch. It should:

1. Create two tickets with different titles.
2. Fill the search box with a partial match for one title.
3. Assert the matching row is visible and the non-matching row is hidden (after the 300 ms debounce).
4. Type a query that matches nothing and assert `#search-empty` is visible.
5. Clear the input and assert both rows are visible again.

This is the single highest-value concept: Playwright's web-first retrying assertions
handle the debounce automatically — no `WebDriverWait`, no `time.sleep`.
