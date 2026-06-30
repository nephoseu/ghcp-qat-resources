"""
Advanced Selenium tests targeting features that require non-trivial migration to Playwright.

Each test exercises a pattern where a naive line-by-line conversion breaks:

  test_confirm_delete_dialog    — switch_to.alert (must come AFTER the click)
  test_ticket_detail_in_iframe  — switch_to.frame / switch_to.default_content
  test_open_ticket_in_new_tab   — window_handles / switch_to.window
  test_toast_auto_dismiss        — WebDriverWait for visibility AND invisibility
  test_shadow_dom_copy_widget   — .shadow_root + find_element inside shadow tree
  test_drag_drop_kanban_close   — ActionChains click_and_hold → move → release
                                   (NOTE: HTML5 drag via ActionChains is known-flaky;
                                   that contrast with Playwright is part of the lesson)

Run headless (default):
    pytest tests/e2e_advanced.py

Run with a visible browser:
    pytest tests/e2e_advanced.py --headed
"""
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from django.contrib.auth.models import User

from tickets.models import Ticket

pytestmark = pytest.mark.django_db(transaction=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser(request):
    headed = request.config.getoption("--headed")
    opts = Options()
    if not headed:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,800")
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(6)
    driver._headed = headed
    yield driver
    driver.quit()


def _pause(driver, seconds=0.6):
    if getattr(driver, "_headed", False):
        time.sleep(seconds)


# ---------------------------------------------------------------------------
# Helpers  (same pattern as tests/e2e.py)
# ---------------------------------------------------------------------------

def _wait_for(driver, element_id, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, element_id))
    )


def _login(driver, base_url, username, password):
    driver.get(f"{base_url}/")
    _wait_for(driver, "login-button")
    _pause(driver)
    field = driver.find_element(By.ID, "username-input")
    field.clear()
    field.send_keys(username)
    driver.find_element(By.ID, "password-input").send_keys(password)
    _pause(driver, 0.4)
    driver.find_element(By.ID, "login-button").click()


def _logout(driver):
    _wait_for(driver, "logout-button")
    _pause(driver)
    driver.find_element(By.ID, "logout-button").click()
    _wait_for(driver, "login-button")


# ---------------------------------------------------------------------------
# Test 1 — Confirm-on-delete JS dialog
#
# Selenium approach: click the button first, THEN switch_to.alert to handle it.
# Playwright approach: register page.on("dialog", …) BEFORE the click — the
# handler must be in place because Playwright fires synchronously.
# ---------------------------------------------------------------------------

def test_confirm_delete_dialog(live_server, browser):
    """Red button triggers confirm(); accepting it deletes the ticket."""
    user = User.objects.create_user(username="adv_confirm", password="pass")
    ticket = Ticket.objects.create(user=user, title="Confirm me", description="pls")

    _login(browser, live_server.url, "adv_confirm", "pass")
    _wait_for(browser, f"confirm-delete-{ticket.id}")
    _pause(browser)

    browser.find_element(By.ID, f"confirm-delete-{ticket.id}").click()

    # In Selenium the dialog is already open — switch_to.alert handles it after the click.
    # (The dialog title reads "TaskDesk says:" instead of "localhost says:".)
    alert = WebDriverWait(browser, 8).until(EC.alert_is_present())
    _pause(browser)
    alert.accept()

    _wait_for(browser, "empty-state")
    assert "No tickets" in browser.find_element(By.ID, "empty-state").text

    _logout(browser)


# ---------------------------------------------------------------------------
# Test 2 — Ticket detail in an iframe
#
# Selenium approach: switch_to.frame(element), interact, switch_to.default_content().
# Playwright approach: page.frame_locator("#ticket-detail-frame").locator(…)
# — no explicit "switch"; frame_locator chains keep context automatically.
# ---------------------------------------------------------------------------

def test_ticket_detail_in_iframe(live_server, browser):
    """Click View → detail page loads in an iframe; assert content inside the frame."""
    user = User.objects.create_user(username="adv_iframe", password="pass")
    ticket = Ticket.objects.create(user=user, title="IFrame Ticket", description="See me inside", severity="high")

    _login(browser, live_server.url, "adv_iframe", "pass")
    _wait_for(browser, f"view-ticket-{ticket.id}")
    _pause(browser)

    browser.find_element(By.ID, f"view-ticket-{ticket.id}").click()
    _pause(browser)

    # Wait for the iframe to gain a src and switch into it.
    frame_elem = WebDriverWait(browser, 10).until(
        lambda d: d.find_element(By.ID, "ticket-detail-frame")
        if d.find_element(By.ID, "ticket-detail-frame").get_attribute("src")
        else None
    )
    browser.switch_to.frame(frame_elem)

    _wait_for(browser, "detail-title")
    assert "IFrame Ticket" in browser.find_element(By.ID, "detail-title").text
    assert browser.find_element(By.ID, "detail-severity").text.lower() == "high"

    # Return to the main document before continuing.
    browser.switch_to.default_content()

    _logout(browser)


# ---------------------------------------------------------------------------
# Test 3 — Open ticket detail in a new tab
#
# Selenium approach: click the link, collect window_handles, switch_to.window(new).
# Playwright approach: context.expect_page() context manager — no handle bookkeeping.
# ---------------------------------------------------------------------------

def test_open_ticket_in_new_tab(live_server, browser):
    """↗ link opens the detail page in a new browser tab."""
    user = User.objects.create_user(username="adv_newtab", password="pass")
    ticket = Ticket.objects.create(user=user, title="New Tab Ticket", description="open me")

    _login(browser, live_server.url, "adv_newtab", "pass")
    _wait_for(browser, f"open-tab-{ticket.id}")
    _pause(browser)

    original_window = browser.current_window_handle
    browser.find_element(By.ID, f"open-tab-{ticket.id}").click()

    # Wait until a second window/tab appears.
    WebDriverWait(browser, 10).until(lambda d: len(d.window_handles) > 1)
    new_window = next(w for w in browser.window_handles if w != original_window)
    browser.switch_to.window(new_window)

    _wait_for(browser, "detail-title")
    _pause(browser)
    assert "New Tab Ticket" in browser.find_element(By.ID, "detail-title").text

    browser.close()
    browser.switch_to.window(original_window)

    _logout(browser)


# ---------------------------------------------------------------------------
# Test 4 — Auto-dismissing toast after ticket submit
#
# Selenium approach: WebDriverWait for visibility_of, then invisibility_of — two
# separate waits, each with a timeout.
# Playwright approach: expect(locator).to_be_visible() then .to_be_hidden() —
# both auto-retry; no explicit condition imports needed.
# ---------------------------------------------------------------------------

def test_toast_auto_dismiss(live_server, browser):
    """Toast appears immediately after submit and disappears within ~4 s."""
    User.objects.create_user(username="adv_toast", password="pass")

    _login(browser, live_server.url, "adv_toast", "pass")
    _wait_for(browser, "ticket-title-input")
    _pause(browser)

    browser.find_element(By.ID, "ticket-title-input").send_keys("Toast Test")
    browser.find_element(By.ID, "ticket-description-input").send_keys("checking toast")
    browser.find_element(By.ID, "submit-ticket-button").click()

    # Wait for the toast to become visible …
    WebDriverWait(browser, 8).until(EC.visibility_of_element_located((By.ID, "toast")))
    assert browser.find_element(By.ID, "toast").is_displayed()

    # … then wait for it to auto-dismiss.
    WebDriverWait(browser, 8).until(EC.invisibility_of_element_located((By.ID, "toast")))
    assert not browser.find_element(By.ID, "toast").is_displayed()

    _logout(browser)


# ---------------------------------------------------------------------------
# Test 5 — Shadow-DOM "copy ID" widget
#
# Selenium approach: get the shadow root via .shadow_root, then find_element
# within that shadow root — two explicit steps.
# Playwright approach: CSS selectors auto-pierce shadow DOM, so
# page.locator("#copy-widget-N .copy-btn").click() works directly.
# ---------------------------------------------------------------------------

def test_shadow_dom_copy_widget(live_server, browser):
    """Clicking the Copy ID button inside the shadow root shows the 'Copied!' message."""
    user = User.objects.create_user(username="adv_shadow", password="pass")
    ticket = Ticket.objects.create(user=user, title="Shadow Ticket", description="copy my id")

    _login(browser, live_server.url, "adv_shadow", "pass")
    _wait_for(browser, f"copy-widget-{ticket.id}")
    _pause(browser)

    # Step 1: find the shadow host element.
    widget = browser.find_element(By.ID, f"copy-widget-{ticket.id}")

    # Step 2: access the shadow root (Selenium 4.x property).
    shadow_root = widget.shadow_root

    # Step 3: find elements inside the shadow tree.
    copy_btn = shadow_root.find_element(By.CSS_SELECTOR, ".copy-btn")
    copy_btn.click()
    _pause(browser, 0.5)

    copied_msg = shadow_root.find_element(By.CSS_SELECTOR, ".copied-msg")
    assert copied_msg.is_displayed(), "'Copied!' message should be visible after click"

    _logout(browser)


# ---------------------------------------------------------------------------
# Test 6 — Drag-and-drop kanban close (admin)
#
# Selenium approach: ActionChains with click_and_hold → move_to_element → release.
# NOTE: Selenium ActionChains simulate mouse events (mousedown/mouseup), not HTML5
# DragEvents — so the board must listen to BOTH event types (it does).
# The implementation is deliberately flakier than Playwright's drag_to();
# that contrast is the teaching point.
#
# Playwright approach: locator.drag_to(target) — uses browser-native drag,
# far more reliable and requires no setup.
# ---------------------------------------------------------------------------

def test_drag_drop_kanban_close(live_server, browser):
    """Dragging a card from the Open column to the Closed column closes the ticket."""
    reg_user = User.objects.create_user(username="adv_drag_user", password="pass")
    admin = User.objects.create_user(username="adv_drag_admin", password="pass", is_staff=True)
    ticket = Ticket.objects.create(user=reg_user, title="Drag To Close", description="drag me")

    _login(browser, live_server.url, "adv_drag_admin", "pass")
    _wait_for(browser, "col-open")
    _wait_for(browser, f"card-{ticket.id}")
    _pause(browser)

    card = browser.find_element(By.ID, f"card-{ticket.id}")
    col_closed = browser.find_element(By.ID, "col-closed")

    # ActionChains mouse simulation — triggers the mousedown/mouseup handlers on the board.
    ActionChains(browser)\
        .move_to_element(card)\
        .click_and_hold()\
        .move_to_element(col_closed)\
        .release()\
        .perform()

    # The board submits a hidden form on mouseup → page reloads with ticket closed.
    _wait_for(browser, "tickets-table")
    _pause(browser)
    status_badge = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, f"ticket-status-{ticket.id}"))
    )
    assert status_badge.text.lower() == "closed"

    _logout(browser)
