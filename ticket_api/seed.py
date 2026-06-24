"""
Seed script — run once before the lab.

    cd ticket_api
    python seed.py
"""
import random

from app.core.security import hash_password
from app.db.models import Ticket, User
from app.db.session import Base, SessionLocal, engine

SEVERITIES = ("critical", "high", "medium", "low")

TITLE_PREFIXES = [
    "Login page", "Dashboard", "Admin panel", "Ticket form", "Search feature",
    "Email notification", "Export CSV", "Bulk action", "Mobile layout", "API timeout",
    "Session expiry", "Password reset", "User profile", "Attachment upload", "PDF export",
    "Dark mode", "Keyboard shortcut", "Browser extension", "WebSocket", "Caching layer",
]

TITLE_SUFFIXES = [
    "throws 500 error", "crashes under load", "returns wrong data", "is unreachable",
    "has broken styling", "not sending emails", "resets on refresh", "ignores filters",
    "times out after 30s", "shows blank page", "missing validation", "leaks memory",
    "breaks on Firefox", "fails silently", "produces duplicates", "truncates output",
    "ignores permissions", "loses state", "renders incorrectly", "blocks main thread",
    "is too slow", "needs caching", "has race condition", "throws 403 randomly",
    "locks the database",
]


def main():
    print("Dropping and recreating tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        user = User(username="user", hashed_password=hash_password("user"), is_admin=False)
        admin = User(username="admin", hashed_password=hash_password("admin"), is_admin=True)
        db.add_all([user, admin])
        db.flush()

        seen_titles: set[str] = set()
        tickets = []
        for i in range(500):
            prefix = TITLE_PREFIXES[i % len(TITLE_PREFIXES)]
            suffix = TITLE_SUFFIXES[i % len(TITLE_SUFFIXES)]
            title = f"{prefix} {suffix} #{i + 1}"
            while title in seen_titles:
                title = f"{prefix} {suffix} #{i + 1} (v{random.randint(2, 99)})"
            seen_titles.add(title)
            tickets.append(Ticket(
                user_id=user.id,
                title=title,
                description=f"Reported in issue #{1000 + i}. Reproducible on all browsers.",
                severity=SEVERITIES[i % len(SEVERITIES)],
                status="open" if i % 5 != 0 else "closed",
            ))

        db.bulk_save_objects(tickets)
        db.commit()
        print("Done. Accounts: user/user (regular), admin/admin (staff). 50 tickets created.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
