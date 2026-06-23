from uuid import uuid4


def test_create_ticket_and_list_it(client, auth_headers):
    marker = uuid4().hex[:8]
    payload = {
        "title": f"lab3-smoke-{marker}",
        "description": "Smoke test ticket from pytest harness",
    }

    create_response = client.post("/tickets/", json=payload, headers=auth_headers)
    assert create_response.status_code == 201
    created_ticket = create_response.json()

    list_response = client.get("/tickets/", headers=auth_headers)
    assert list_response.status_code == 200
    tickets = list_response.json()

    assert any(ticket["id"] == created_ticket["id"] for ticket in tickets)
    assert any(ticket["title"] == payload["title"] for ticket in tickets)
