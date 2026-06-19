import os

# pytest-playwright runs an async event loop; allow Django sync DB ops inside it.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

# pytest-django reads DJANGO_SETTINGS_MODULE from pytest.ini.
# --headed flag is provided by pytest-playwright and shared by both test files.
