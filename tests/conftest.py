# pytest-django reads DJANGO_SETTINGS_MODULE from pytest.ini.

def pytest_addoption(parser):
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run Selenium tests in a visible browser window",
    )
