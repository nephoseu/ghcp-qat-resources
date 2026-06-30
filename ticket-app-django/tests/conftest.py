import os

# pytest-playwright runs an async event loop; allow Django sync DB ops inside it.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

# pytest-django reads DJANGO_SETTINGS_MODULE from pytest.ini.


def pytest_addoption(parser):
    # Register --headed so Selenium tests work even without pytest-playwright installed.
    # pytest-playwright also registers this flag; the except block handles double-registration.
    try:
        parser.addoption(
            "--headed",
            action="store_true",
            default=False,
            help="Run browser with a visible window (Selenium and Playwright)",
        )
    except Exception:
        pass  # Already registered by pytest-playwright
