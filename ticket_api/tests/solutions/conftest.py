import os

import httpx
import pytest

from .factories import make_ticket


BASE_URL = os.getenv("TASKDESK_BASE_URL", "http://localhost:8081")


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def auth_headers(client):
    response = client.post(
        "/auth/login",
        data={"username": "user", "password": "user"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def ticket_factory(client, auth_headers):
    def _create(count=1, **overrides):
        created = []
        for _ in range(count):
            payload = make_ticket(**overrides)
            response = client.post("/tickets/", json=payload, headers=auth_headers)
            assert response.status_code == 201, response.text
            created.append(response.json())
        return created

    return _create
