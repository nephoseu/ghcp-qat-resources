# Lab 3 Selenium to Playwright Migration with GitHub Copilot

## Overview

You will migrate an existing Selenium test suite to Playwright in three stages: a straightforward conversion, a set of patterns where naive migration breaks, and finally writing a brand-new test from scratch. GitHub Copilot is your assistant throughout — but you will need to know enough to steer it and fix what it gets wrong.

**App under test:** TaskDesk — a ticket management system  
**Estimated time:** 60–90 minutes

!!! tip "Download the app first"
    Lab 3 uses **TaskDesk (Django)**. Download and unzip it before following the setup steps below.

    [Download taskdesk-django.zip](https://github.com/nephoseu/ghcp-qat-resources/releases/latest/download/taskdesk-django.zip){ .md-button }

---

## Setup

### 1. Enter the project and create a virtual environment

```bash
cd ghcp-qat-resources

python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright

Playwright is **not** in `requirements.txt` — it is separate from the Selenium setup. Install it and download the browser binaries:

```bash
pip install playwright==1.60.0 pytest-playwright==0.8.0
playwright install chromium
```

### 4. Set up the database and start the app

```bash
python manage.py migrate
python manage.py seed             # creates demo accounts and sample tickets
python manage.py runserver 0.0.0.0:8080
```

Open `http://localhost:8080` in your browser. You should see the TaskDesk login page.

> Run `python manage.py seed --clear` to wipe all tickets and start fresh.

**Demo accounts:**

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

## Task 1 — Basic Migration with Copilot

**Source:** `tests/e2e.py`  
**Target:** `tests/test_task1_playwright.py` *(create this file)*

### Goal

Use GitHub Copilot to convert the five existing Selenium tests into Playwright. This is the straightforward case — every element has a stable `id` and the flows map almost directly.

### How to approach it

1. Open `tests/e2e.py` alongside your new file.
2. For each test, let Copilot suggest the Playwright version. Accept what makes sense, correct what does not.
3. Pay attention to what Copilot removes vs. what it keeps — it should drop the explicit waits and the `By.ID` imports.

### Things to know going in

- The `browser` fixture from `e2e.py` is replaced by `page` — provided automatically by `pytest-playwright`.
- Playwright has no `WebDriverWait`. Assertions automatically retry until the condition is met.
- Use `expect(locator).to_...()` for assertions instead of plain `assert`.
- Drop-down selection: `locator.select_option("value")` instead of `Select(el).select_by_value(...)`.

### Run your tests

```bash
pytest tests/test_task1_playwright.py --headed --slowmo 500
```

---

## Task 2 — Advanced Migration

**Source:** `tests/e2e_advanced.py`  
**Target:** `tests/test_task2_playwright.py` *(create this file)*

### Goal

Migrate six Selenium tests that cover patterns where a direct translation breaks. Copilot will get some of these partially right and others completely wrong. Your job is to recognise what is broken and fix it.

Work through each test in order. Read the description of the concept first, then write the code.

---

### Test 1 — Confirm dialog (`test_confirm_delete_dialog`)

The red **Delete!** button on each ticket row triggers a native browser `confirm()` dialog.

In Selenium you handle the dialog *after* the click. In Playwright the handler must be registered *before* — Playwright fires it synchronously the moment the dialog opens, so anything registered after the click is already too late.

**Element:** `#confirm-delete-{id}`  
**Hint:** Look up `page.on("dialog", ...)` and pay close attention to where you place that line relative to the click.

---

### Test 2 — Iframe (`test_ticket_detail_in_iframe`)

The **View** button per row loads the ticket detail page inside a `#ticket-detail-frame` iframe embedded on the same page.

Selenium requires you to switch context into the frame with `switch_to.frame()`, interact, then switch back with `switch_to.default_content()`. Playwright has no switching — it has `frame_locator()`, which returns a locator scoped to the frame content.

**Elements:** `#view-ticket-{id}`, `#ticket-detail-frame`, `#detail-title`  
**Hint:** Chain `page.frame_locator(...)` and then use `.locator(...)` on the result.

---

### Test 3 — New tab (`test_open_ticket_in_new_tab`)

The **↗** link opens the ticket detail page in a new browser tab (`target="_blank"`).

Selenium requires you to track `window_handles` before and after the click, diff them to find the new handle, and then call `switch_to.window()`. Playwright gives you the new `Page` object directly through a context manager.

**Elements:** `#open-tab-{id}`, `#detail-title`  
**Hint:** Look up `page.context.expect_page()`.

---

### Test 4 — Auto-dismissing toast (`test_toast_auto_dismiss`)

After submitting a ticket, a toast notification appears at the bottom-right of the screen and disappears automatically after 3 seconds.

In Selenium you need two separate `WebDriverWait` calls — one to wait for the toast to appear, one to wait for it to disappear. In Playwright, two `expect()` assertions handle both — no extra imports, no condition objects.

**Element:** `#toast`  
**Hint:** `to_be_visible()` and `to_be_hidden()` both auto-retry. For `to_be_hidden()`, set a timeout that gives the 3-second timer enough room.

---

### Test 5 — Shadow DOM (`test_shadow_dom_copy_widget`)

Each ticket row has a **Copy ID** button rendered inside a shadow DOM web component (`<copy-id-widget id="copy-widget-{id}">`). Clicking it shows a **Copied!** message.

Selenium requires you to explicitly retrieve the shadow root and then find elements within it as a separate step. Playwright's CSS locator engine automatically pierces shadow DOM — you can target elements inside a shadow root the same way as any other element.

**Elements:** `#copy-widget-{id}`, `.copy-btn`, `.copied-msg`  
**Hint:** You do not need anything special — just write the selector.

---

### Test 6 — Drag-and-drop kanban (`test_drag_drop_kanban_close`)

On the admin dashboard there is a two-column kanban board. Dragging a card from the **Open** column (`#col-open`) to the **Closed** column (`#col-closed`) closes the ticket.

Selenium's `ActionChains` simulates mouse events but does **not** fire HTML5 drag events. The board supports both event types for this reason, so ActionChains works here — but it is notoriously flaky. Playwright's `drag_to()` uses the browser's native drag mechanism and is significantly more reliable.

**Elements:** `#card-{id}`, `#col-closed`, `#ticket-status-{id}`  
**Hint:** `locator.drag_to(target_locator)` — one line.

---

### Run your tests

```bash
pytest tests/test_task2_playwright.py --headed --slowmo 500
```

### Done when

All six tests pass. The instructor answer key is at `tests/solutions/solution_advanced_playwright.py` — check it only after a genuine attempt.

---

## Task 3 — Write a Test from Scratch

**Target:** `tests/test_task3_search.py` *(create this file)*

### Goal

Write a Playwright test for the live search filter on the user dashboard — entirely from scratch, without a Selenium version to convert.

### What the feature does

The `#ticket-search-input` field filters the tickets table in real time:

- Rows whose title does not match the query are hidden after a 300 ms debounce.
- When no rows match, the message `#search-empty` becomes visible.
- Clearing the input restores all rows and hides `#search-empty`.

### Your test should

1. Create (at least) two tickets with different titles.
2. Log in as the ticket owner.
3. Type a partial query that matches only one title.
4. Assert the matching row is visible and the non-matching row is hidden.
5. Type a query that matches nothing.
6. Assert `#search-empty` is visible.
7. Clear the input and assert both rows are visible again.

### Useful selectors

| What | Selector |
|------|----------|
| Search input | `#ticket-search-input` |
| A specific ticket row | `tr[data-title="Exact Title Here"]` |
| No-match message | `#search-empty` |

### The key concept

Do not add `time.sleep(0.3)` for the debounce delay. Playwright's web-first assertions retry automatically — `expect(locator).to_be_hidden()` will keep checking until the row disappears or the timeout expires, naturally absorbing the debounce.

### Run your test

```bash
pytest tests/test_task3_search.py --headed --slowmo 500
```

### Done when

Your test passes. Then compare it with `test_live_search_filter` in `tests/solutions/solution_advanced_playwright.py`.

---

## Quick reference

### Running tests

```bash
# Single file, visible browser
pytest tests/test_task1_playwright.py --headed

# Visible browser with slow-motion (ms between actions)
pytest tests/test_task2_playwright.py --headed --slowmo 600

# Debug mode — opens Playwright Inspector, steps through each action
PWDEBUG=1 pytest tests/test_task2_playwright.py -k test_confirm_delete_dialog

# Choose a different browser
pytest tests/test_task1_playwright.py --browser firefox
```

### Key Selenium → Playwright differences

| Concept | Selenium | Playwright |
|---------|----------|------------|
| Find element | `driver.find_element(By.ID, "x")` | `page.locator("#x")` |
| Wait for element | `WebDriverWait(driver, 8).until(EC.presence_of_element_located(...))` | *(built-in on every action)* |
| Assert text | `assert "text" in el.text` | `expect(locator).to_contain_text("text")` |
| Assert visible | `assert el.is_displayed()` | `expect(locator).to_be_visible()` |
| Select dropdown | `Select(el).select_by_value("v")` | `locator.select_option("v")` |
| Dialog | click → `switch_to.alert` → accept | `page.on("dialog", ...)` → click |
| Iframe | `switch_to.frame(el)` / `switch_to.default_content()` | `page.frame_locator("#id").locator(...)` |
| New tab | `window_handles` diff → `switch_to.window()` | `page.context.expect_page()` |
| Shadow DOM | `el.shadow_root.find_element(...)` | CSS pierces automatically |
| Drag and drop | `ActionChains(...).drag_and_drop(...)` | `locator.drag_to(target)` |
