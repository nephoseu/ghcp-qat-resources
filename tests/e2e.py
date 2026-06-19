"""
Selenium tests covering:
  - Auth flow (login → dashboard → logout)
  - User submitting a ticket
  - User deleting a ticket
  - Admin login + closing a ticket

Run headless (default):
    pytest tests/test_selenium.py

Run with a visible browser:
    pytest tests/test_selenium.py --headed
"""
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    """Small delay when running headed so steps are visible."""
    if getattr(driver, "_headed", False):
        time.sleep(seconds)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wait_for(driver, element_id, timeout=8):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, element_id))
    )


def _login(driver, base_url, username, password):
    driver.get(f"{base_url}/")
    _wait_for(driver, "login-button")
    _pause(driver)
    username_field = driver.find_element(By.ID, "username-input")
    username_field.clear()
    username_field.send_keys(username)
    _pause(driver, 0.4)
    password_field = driver.find_element(By.ID, "password-input")
    password_field.clear()
    password_field.send_keys(password)
    _pause(driver, 0.4)
    driver.find_element(By.ID, "login-button").click()


def _logout(driver):
    _wait_for(driver, "logout-button")
    _pause(driver)
    driver.find_element(By.ID, "logout-button").click()
    _wait_for(driver, "login-button")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_auth_flow(live_server, browser):
    """Login as a regular user then log out — verifies welcome label and redirect."""
    User.objects.create_user(username="sel_auth", password="sel_pass")

    _login(browser, live_server.url, "sel_auth", "sel_pass")
    _wait_for(browser, "welcome-label")
    assert "sel_auth" in browser.find_element(By.ID, "welcome-label").text

    _logout(browser)
    assert browser.find_element(By.ID, "login-button")


def test_invalid_login_shows_error(live_server, browser):
    """Wrong password shows the error message."""
    User.objects.create_user(username="sel_invalid", password="correct")

    _login(browser, live_server.url, "sel_invalid", "wrong_password")
    _wait_for(browser, "login-error")
    assert browser.find_element(By.ID, "login-error").is_displayed()


def test_user_submit_ticket(live_server, browser):
    """User fills in the ticket form — ticket appears in the table."""
    User.objects.create_user(username="sel_submit", password="sel_pass")

    _login(browser, live_server.url, "sel_submit", "sel_pass")
    _wait_for(browser, "ticket-title-input")
    _pause(browser)

    browser.find_element(By.ID, "ticket-title-input").send_keys("Login broken")
    _pause(browser, 0.4)
    browser.find_element(By.ID, "ticket-description-input").send_keys("Cannot log in to prod")
    _pause(browser, 0.4)
    from selenium.webdriver.support.ui import Select
    Select(browser.find_element(By.ID, "ticket-severity-select")).select_by_value("critical")
    _pause(browser, 0.4)
    browser.find_element(By.ID, "submit-ticket-button").click()

    _wait_for(browser, "tickets-table")
    _pause(browser)
    assert "Login broken" in browser.find_element(By.ID, "tickets-table").text

    _logout(browser)


def test_user_delete_ticket(live_server, browser):
    """User deletes a ticket — empty state is shown afterwards."""
    user = User.objects.create_user(username="sel_delete", password="sel_pass")
    ticket = Ticket.objects.create(user=user, title="To be deleted", description="bye")

    _login(browser, live_server.url, "sel_delete", "sel_pass")
    _wait_for(browser, f"delete-ticket-{ticket.id}")
    _pause(browser)

    browser.find_element(By.ID, f"delete-ticket-{ticket.id}").click()

    _wait_for(browser, "empty-state")
    _pause(browser)
    assert "No tickets" in browser.find_element(By.ID, "empty-state").text

    _logout(browser)


def test_admin_login_and_close_ticket(live_server, browser):
    """Admin logs in, sees a user's ticket, closes it — status badge updates."""
    user = User.objects.create_user(username="sel_user_close", password="user_pass")
    User.objects.create_user(username="sel_admin_close", password="admin_pass", is_staff=True)
    ticket = Ticket.objects.create(user=user, title="Needs closing", description="Please close me")

    _login(browser, live_server.url, "sel_admin_close", "admin_pass")
    _wait_for(browser, "tickets-table")
    _pause(browser)
    assert "Needs closing" in browser.find_element(By.ID, "tickets-table").text

    browser.find_element(By.ID, f"close-ticket-{ticket.id}").click()
    
    _pause(browser)
    assert browser.find_element(By.ID, f"ticket-status-{ticket.id}").text.lower() == "closed"

    _logout(browser)
