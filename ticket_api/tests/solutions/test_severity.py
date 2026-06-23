import pytest

from .factories import make_ticket


@pytest.mark.parametrize("severity", ["critical", "high", "medium", "low"])
def test_create_ticket_with_valid_severity(client, auth_headers, severity):
    payload = make_ticket(severity=severity)

    response = client.post("/tickets/", json=payload, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["severity"] == severity


@pytest.mark.parametrize("severity", ["", "urgent", "HIGH"])
def test_create_ticket_with_invalid_severity(client, auth_headers, severity):
    payload = make_ticket(severity=severity)

    response = client.post("/tickets/", json=payload, headers=auth_headers)

    assert response.status_code == 400
