from uuid import uuid4

import pytest


@pytest.mark.parametrize(
    "query, expected_match",
    [
        ("exact-marker", True),
        ("upper-marker", True),
        ("no-match", False),
    ],
)
def test_search_returns_only_marker_tagged_tickets(
    client,
    auth_headers,
    ticket_factory,
    query,
    expected_match,
):
    marker = f"lab3-{uuid4().hex[:8]}"
    created = ticket_factory(count=3, marker=marker)

    if query == "exact-marker":
        effective_query = marker
    elif query == "upper-marker":
        effective_query = marker.upper()
    else:
        effective_query = f"missing-{marker}"

    response = client.get(
        "/tickets/search",
        params={"q": effective_query},
        headers=auth_headers,
    )

    assert response.status_code == 200
    result_ids = {ticket["id"] for ticket in response.json()}
    created_ids = {ticket["id"] for ticket in created}

    if expected_match:
        assert created_ids.issubset(result_ids)
    else:
        assert created_ids.isdisjoint(result_ids)
