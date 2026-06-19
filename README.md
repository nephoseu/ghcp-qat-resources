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
│           └── admin_dashboard.html
└── tests/
    └── test_selenium.py   # End-to-end Selenium tests (Chrome required)
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

### Selenium tests

#### Requirements

| Requirement | Details |
|-------------|---------|
| **Google Chrome** | Any recent version (v115+). Download from [google.com/chrome](https://www.google.com/chrome/) |
| **ChromeDriver** | **Not needed — Selenium Manager (bundled since Selenium 4.6) downloads the matching driver automatically** when the tests first run. You only need Chrome itself installed. |
| **Python 3.10+** | The project targets Python 3.13 |
| **`selenium` package** | Installed via `requirements.txt` |

> **Using a different browser?**
> The tests are written for Chrome. To use Firefox instead, swap `webdriver.Chrome` for `webdriver.Firefox` and `Options` from `selenium.webdriver.firefox.options`. Firefox requires **geckodriver** — download it from [github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases) and place it on your `PATH`. Selenium Manager can also download geckodriver automatically in most cases.

#### Run headless (default — no window, fastest)

```bash
pytest tests/test_selenium.py
```

#### Run with a visible browser window

```bash
pytest tests/test_selenium.py --headed
```

Steps are slowed down slightly so you can follow what Selenium is doing.

#### Run everything

```bash
pytest tests/
```

---

## URL reference

| URL | Method | Description |
|-----|--------|-------------|
| `/` | GET, POST | Login page |
| `/logout/` | POST | Sign out |
| `/dashboard/` | GET, POST | User dashboard — list and submit tickets |
| `/tickets/<id>/delete/` | POST | Delete a ticket (owner only) |
| `/admin-dashboard/` | GET | Admin view — all tickets |
| `/tickets/<id>/close/` | POST | Close a ticket (admin only) |

---

## Selenium element IDs

All stable `id` attributes for test selectors:

| Element | ID |
|---------|----|
| Username input | `username-input` |
| Password input | `password-input` |
| Login button | `login-button` |
| Login error message | `login-error` |
| Welcome label | `welcome-label` |
| Logout button | `logout-button` |
| Ticket title input | `ticket-title-input` |
| Ticket description input | `ticket-description-input` |
| Submit ticket button | `submit-ticket-button` |
| Tickets table | `tickets-table` |
| Delete button (per row) | `delete-ticket-{id}` |
| Close button (admin, per row) | `close-ticket-{id}` |
| Ticket status (admin, per row) | `ticket-status-{id}` |
| Empty state message | `empty-state` |
