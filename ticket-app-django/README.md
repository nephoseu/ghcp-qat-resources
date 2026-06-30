# TaskDesk — Django App

A ticket management web app built with **Django 5.2** and **SQLite**. Designed as the test target for **Lab 3** (Selenium → Playwright migration) — every interactive element has a stable `id` attribute.

## What it does

- **Regular users** can sign in, submit support tickets, and delete their own tickets.
- **Admins** see all tickets from all users and can close them. Admins cannot submit tickets.
- Two roles are fully separated — each lands on a different page after login.

### Seeded accounts

| Username | Password | Role  |
|----------|----------|-------|
| `user`   | `user`   | User  |
| `admin`  | `admin`  | Admin |

---

## Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run database migrations

```bash
python manage.py migrate
```

### 4. Start the development server

```bash
python manage.py runserver 0.0.0.0:8080
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

> Run `python manage.py seed --clear` to wipe all tickets and start fresh.

---

## Running the tests

### Baseline Selenium tests

```bash
pytest tests/e2e.py
pytest tests/e2e.py --headed
```

### Advanced Selenium tests (migration lab)

```bash
pytest tests/e2e_advanced.py
pytest tests/e2e_advanced.py --headed
```

### Playwright (install separately)

```bash
pip install playwright==1.60.0 pytest-playwright==0.8.0
playwright install chromium

pytest tests/solutions/solution_advanced_playwright.py --headed --slowmo 600
```

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
| Toast notification | `toast` |
| Search input | `ticket-search-input` |
| No-match message | `search-empty` |
| Confirm-delete button (per row) | `confirm-delete-{id}` |
| View-in-iframe button (per row) | `view-ticket-{id}` |
| Iframe container | `ticket-detail-frame` |
| Open-in-new-tab link (per row) | `open-tab-{id}` |
| Shadow-DOM copy-ID widget (per row) | `copy-widget-{id}` |
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
| Kanban open column | `col-open` |
| Kanban closed column | `col-closed` |
| Kanban card (per ticket) | `card-{id}` |

### Ticket detail page

| Element | ID |
|---------|----|
| Title | `detail-title` |
| Description | `detail-description` |
| Severity badge | `detail-severity` |
| Status badge | `detail-status` |
| Close button | `close-detail-button` |

---

## Advanced migration patterns

`tests/e2e_advanced.py` contains six Selenium tests that cover patterns where a naive line-by-line conversion to Playwright breaks:

| Test | Feature | What breaks in naive conversion |
|------|---------|----------------------------------|
| `test_confirm_delete_dialog` | JS `confirm()` dialog | `page.on("dialog")` must be registered **before** the click |
| `test_ticket_detail_in_iframe` | Iframe content | `switch_to.frame` vs `frame_locator()` |
| `test_open_ticket_in_new_tab` | `target=_blank` link | `window_handles` vs `context.expect_page()` |
| `test_toast_auto_dismiss` | Auto-dismissing toast | Two `WebDriverWait` calls vs two `expect()` assertions |
| `test_shadow_dom_copy_widget` | Shadow DOM widget | `.shadow_root` traversal vs automatic CSS piercing |
| `test_drag_drop_kanban_close` | Kanban drag-and-drop | `ActionChains` vs `drag_to()` |
