"""
Seed script — run once before the lab.

    cd ticket-api-lab5
    python seed.py
"""
import random
from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.db.models import Category, Comment, Ticket, User
from app.db.session import Base, SessionLocal, engine

SEVERITIES = ("critical", "high", "medium", "low")

# name, sla_hours
CATEGORIES = [
    ("Authentication", 4),
    ("Billing", 8),
    ("Infrastructure", 24),
    ("Mobile", 48),
    ("Reporting", 72),
    ("Integrations", 96),
]

# Repeating cycle of statuses applied across the 500 seeded tickets. "open" appears
# twice so roughly 40% of tickets stay open, matching a realistic backlog shape.
STATUS_CYCLE = ("open", "open", "in_progress", "resolved", "closed")

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

COMMENT_BODIES = [
    "Confirmed on staging, moving forward.",
    "Reproduced locally, investigating root cause.",
    "Waiting on customer confirmation before closing.",
    "Fix verified, no regressions found.",
    "Escalated to the infrastructure team.",
    "Duplicate of an earlier report, merging notes here.",
    "Root cause identified, patch incoming.",
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

        categories = [Category(name=name, sla_hours=sla) for name, sla in CATEGORIES]
        db.add_all(categories)
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

            # Explicit, strictly-increasing timestamps: guarantees deterministic
            # oldest-first ordering regardless of how fast the loop runs.
            created_at = datetime.now(timezone.utc) - timedelta(minutes=(500 - i))

            tickets.append(Ticket(
                user_id=user.id,
                category_id=categories[i % len(categories)].id,
                title=title,
                description=f"Reported in issue #{1000 + i}. Reproducible on all browsers.",
                severity=SEVERITIES[i % len(SEVERITIES)],
                status=STATUS_CYCLE[i % len(STATUS_CYCLE)],
                created_at=created_at,
            ))

        db.add_all(tickets)
        db.flush()

        # Sprinkle comments: every resolved/closed ticket gets a resolution note (the
        # modern API requires >=1 comment before a ticket can move to "resolved"), plus
        # a handful of open/in_progress tickets get an early comment for realism.
        comments = []
        for i, ticket in enumerate(tickets):
            if ticket.status in ("resolved", "closed"):
                comments.append(Comment(
                    ticket_id=ticket.id,
                    author_id=user.id,
                    body=random.choice(COMMENT_BODIES),
                ))
                if ticket.status == "closed" and i % 3 == 0:
                    comments.append(Comment(
                        ticket_id=ticket.id,
                        author_id=admin.id,
                        body="Closing this out after final review.",
                    ))
            elif i % 7 == 0:
                comments.append(Comment(
                    ticket_id=ticket.id,
                    author_id=user.id,
                    body=random.choice(COMMENT_BODIES),
                ))

        db.add_all(comments)
        db.commit()
        print(
            f"Done. Accounts: user/user (regular), admin/admin (staff). "
            f"{len(categories)} categories, {len(tickets)} tickets, "
            f"{len(comments)} comments created."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
