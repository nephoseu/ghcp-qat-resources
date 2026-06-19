"""
Playwright e2e tests covering:
  - Auth flow (login → dashboard → logout)
  - Invalid login shows error
  - User submitting a ticket
  - User deleting a ticket
  - Admin login + closing a ticket

Run headless (default):
    pytest tests/e2e-playwright.py

Run with a visible browser:
    pytest tests/e2e-playwright.py --headed

Run with slow-mo so you can follow each step (ms between actions):
    pytest tests/e2e-playwright.py --headed --slowmo 600

Debug mode — pauses at every action with the Playwright Inspector:
    PWDEBUG=1 pytest tests/e2e-playwright.py

Choose a different browser:
    pytest tests/e2e-playwright.py --browser firefox
    pytest tests/e2e-playwright.py --browser webkit
"""
import pytest
from playwright.sync_api import Page, expect
from django.contrib.auth.models import User

from tickets.models import Ticket

pytestmark = pytest.mark.django_db(transaction=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {**browser_type_launch_args, "slow_mo": 500}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _login(page: Page, base_url: str, username: str, password: str) -> None:
    page.goto(f"{base_url}/")
    page.locator("#username-input").fill(username)
    page.locator("#password-input").fill(password)
    page.locator("#login-button").click()


def _logout(page: Page) -> None:
    page.locator("#logout-button").click()
    expect(page.locator("#login-button")).to_be_visible()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_auth_flow(live_server, page: Page):
    """Login as a regular user then log out — verifies welcome label and redirect."""
    User.objects.create_user(username="pw_auth", password="pw_pass")

    _login(page, live_server.url, "pw_auth", "pw_pass")
    expect(page.locator("#welcome-label")).to_contain_text("pw_auth")

    _logout(page)
    expect(page.locator("#login-button")).to_be_visible()


def test_invalid_login_shows_error(live_server, page: Page):
    """Wrong password shows the error message."""
    User.objects.create_user(username="pw_invalid", password="correct")

    _login(page, live_server.url, "pw_invalid", "wrong_password")
    expect(page.locator("#login-error")).to_be_visible()


def test_user_submit_ticket(live_server, page: Page):
    """User fills in the ticket form — ticket appears in the table."""
    User.objects.create_user(username="pw_submit", password="pw_pass")

    _login(page, live_server.url, "pw_submit", "pw_pass")
    expect(page.locator("#ticket-title-input")).to_be_visible()

    page.locator("#ticket-title-input").fill("Login broken")
    page.locator("#ticket-description-input").fill("Cannot log in to prod")
    page.locator("#ticket-severity-select").select_option("critical")
    page.locator("#submit-ticket-button").click()

    expect(page.locator("#tickets-table")).to_contain_text("Login broken")


def test_user_delete_ticket(live_server, page: Page):
    """User deletes a ticket — empty state is shown afterwards."""
    user = User.objects.create_user(username="pw_delete", password="pw_pass")
    ticket = Ticket.objects.create(user=user, title="To be deleted", description="bye")

    _login(page, live_server.url, "pw_delete", "pw_pass")
    page.locator(f"#delete-ticket-{ticket.id}").click()

    expect(page.locator("#empty-state")).to_contain_text("No tickets")


def test_admin_login_and_close_ticket(live_server, page: Page):
    """Admin logs in, sees a user's ticket, closes it — status badge updates."""
    user = User.objects.create_user(username="pw_user_close", password="user_pass")
    User.objects.create_user(username="pw_admin_close", password="admin_pass", is_staff=True)
    ticket = Ticket.objects.create(user=user, title="Needs closing", description="Please close me")

    _login(page, live_server.url, "pw_admin_close", "admin_pass")
    expect(page.locator("#tickets-table")).to_contain_text("Needs closing")

    page.locator(f"#close-ticket-{ticket.id}").click()

    expect(page.locator(f"#ticket-status-{ticket.id}")).to_have_text("closed", ignore_case=True)
