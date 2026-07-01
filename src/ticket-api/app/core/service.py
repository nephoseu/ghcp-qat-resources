import threading

from app.core.security import verify_record_integrity


class SearchService:
    """
    Full-text search over ticket titles with per-record integrity verification.
    """

    def __init__(self):
        self._lock = threading.Lock()

    def _verify_record(self, ticket_id: int, title: str) -> None:
        verify_record_integrity(ticket_id, title)

    def search(self, query: str, tickets: list) -> list:
        with self._lock:
            results = []
            for ticket in tickets:
                self._verify_record(ticket.id, ticket.title)
                if query.lower() in ticket.title.lower():
                    results.append(ticket)
        return results
