# Lab: Playwright E2E Tests

Playwright is a browser automation framework from Microsoft. Compared to Selenium it has built-in auto-waiting (no explicit `WebDriverWait` needed), a `--headed` / `--slowmo` / debug mode out of the box, and `expect()` assertions that retry until the condition is met or times out.

---

## Requirements

| Requirement | Details |
|-------------|---------|
| **Python 3.10+** | Project targets Python 3.13 |
| **`playwright` package** | Core library (`pip install playwright`) |
| **`pytest-playwright` package** | pytest integration (`pip install pytest-playwright`) |
| **Browser binaries** | Downloaded separately via `playwright install` — **not bundled with the pip package** |

> Unlike Selenium, Playwright ships its own browser builds (Chromium, Firefox, WebKit). You do **not** need Chrome, ChromeDriver, or geckodriver installed on the system. Playwright downloads and manages everything itself.

---

## Installation

### 1. Activate your virtual environment

```bash
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate        # Windows
```

### 2. Install the packages

```bash
pip install playwright==1.60.0 pytest-playwright==0.8.0
```

Or just run:

```bash
pip install -r requirements.txt
```

### 3. Download browser binaries

This step is **required** and separate from the pip install. Run once after installing the package:

```bash
# Chromium only (smallest download, ~100 MB)
playwright install chromium

# All browsers (Chromium + Firefox + WebKit, ~500 MB)
playwright install

# On Linux you may also need system dependencies
playwright install --with-deps chromium
```

Binaries are stored in `~/.cache/ms-playwright/` (Linux/macOS) or `%USERPROFILE%\AppData\Local\ms-playwright\` (Windows). You only need to run this once per machine or after upgrading `playwright`.

---

## Running the tests

### Headless (default — no window, fastest)

```bash
pytest tests/e2e-playwright.py
```

### Visible browser window

```bash
pytest tests/e2e-playwright.py --headed
```

### Visible browser with slow-motion

Slow-mo adds a delay (in milliseconds) between every action so you can follow what Playwright is doing:

```bash
pytest tests/e2e-playwright.py --headed --slowmo 600
```

### Choose a different browser

```bash
pytest tests/e2e-playwright.py --browser firefox
pytest tests/e2e-playwright.py --browser webkit    # Safari engine
pytest tests/e2e-playwright.py --browser chromium  # default
```

### Debug mode — Playwright Inspector

Pauses before every action and opens the Playwright Inspector GUI where you can step through the test, inspect the DOM, and pick locators interactively:

```bash
PWDEBUG=1 pytest tests/e2e-playwright.py -k test_auth_flow
```

### Run both Selenium and Playwright suites together

```bash
pytest tests/
```

---

## Test file overview (`tests/e2e-playwright.py`)

| Test | What it covers |
|------|----------------|
| `test_auth_flow` | Login → welcome label contains username → logout |
| `test_invalid_login_shows_error` | Wrong password → `#login-error` visible |
| `test_user_submit_ticket` | Fill form → ticket appears in `#tickets-table` |
| `test_user_delete_ticket` | Delete ticket → `#empty-state` shown |
| `test_admin_login_and_close_ticket` | Admin closes ticket → status badge = `closed` |

---

## Key differences vs Selenium (`tests/e2e.py`)

| | Selenium | Playwright |
|-|----------|------------|
| Browser driver | ChromeDriver (auto-downloaded by Selenium Manager) | Playwright's own Chromium build |
| Waiting strategy | `WebDriverWait` + `expected_conditions` | Built-in auto-wait on every action |
| Assertions | Plain `assert` + `.text` | `expect(locator).to_contain_text(...)` with retry |
| `--headed` flag | Custom `--headed` option in `conftest.py` | Built in via `pytest-playwright` |
| Slow-mo | Manual `time.sleep()` calls | `--slowmo <ms>` flag |
| Debug / step-through | None built in | `PWDEBUG=1` opens Inspector |
| Multi-browser | Chrome only (configurable manually) | `--browser chromium/firefox/webkit` |

---

## Troubleshooting

**`SynchronousOnlyOperation` error**
Playwright's async event loop conflicts with Django's synchronous DB setup. The fix is already in `tests/conftest.py`:
```python
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
```

**`playwright install` not found after `pip install playwright`**
The `playwright` CLI is installed into the venv's `bin/` directory. Make sure the venv is activated, or call it directly:
```bash
python -m playwright install chromium
```

**Tests run but browser doesn't appear with `--headed`**
On Linux (CI / headless servers) a display is required. Use a virtual display:
```bash
xvfb-run pytest tests/e2e-playwright.py --headed
```
