from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from tickets.models import Ticket


TICKETS = [
    {
        "username": "user",
        "title": "Login page throws 500 on empty password",
        "description": (
            "Submitting the login form with the password field left blank causes "
            "an internal server error instead of showing a validation message. "
            "Reproducible on Chrome and Firefox."
        ),
        "severity": "critical",
        "status": "open",
    },
    {
        "username": "user",
        "title": "Dashboard search resets on page refresh",
        "description": (
            "After typing a search query the results filter correctly, but if the "
            "user refreshes the browser the input clears and all tickets are shown "
            "again. The query should be preserved in the URL."
        ),
        "severity": "medium",
        "status": "open",
    },
    {
        "username": "user",
        "title": "Ticket severity badge colour wrong for High",
        "description": (
            "The 'High' severity badge renders with the same orange colour as "
            "'Critical'. It should use a distinct amber/yellow so users can tell "
            "the two apart at a glance."
        ),
        "severity": "high",
        "status": "open",
    },
    {
        "username": "user",
        "title": "Email notification not sent after ticket is closed",
        "description": (
            "When an admin closes a ticket the reporter no longer receives a "
            "confirmation email. This worked before the last deployment. Checked "
            "the mail log — no outbound messages are queued."
        ),
        "severity": "high",
        "status": "closed",
    },
    {
        "username": "user",
        "title": "Tooltip text cut off on mobile screens",
        "description": (
            "On viewports narrower than 400 px the action-button tooltips overflow "
            "the screen edge. Text beyond the edge is not visible and cannot be "
            "scrolled to."
        ),
        "severity": "low",
        "status": "open",
    },
    {
        "username": "admin",
        "title": "Admin: bulk-close action silently fails for 50+ tickets",
        "description": (
            "Selecting more than 50 tickets and using the bulk 'Close selected' "
            "action returns HTTP 200 but no tickets are updated. Likely a query "
            "timeout or a missing pagination loop in the bulk handler."
        ),
        "severity": "critical",
        "status": "open",
    },
    {
        "username": "admin",
        "title": "Export CSV includes deleted user records",
        "description": (
            "The CSV export pulls tickets from all users including accounts that "
            "were deleted via the admin panel. Those rows have blank username "
            "fields, which breaks downstream import scripts."
        ),
        "severity": "medium",
        "status": "open",
    },
]


class Command(BaseCommand):
    help = "Seed the database with demo accounts and sample tickets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing tickets and non-superuser accounts before seeding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Ticket.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write("Cleared existing tickets and accounts.")

        # Ensure demo accounts exist.
        user, created = User.objects.get_or_create(username="user")
        if created or not user.check_password("user"):
            user.set_password("user")
            user.save()

        admin, created = User.objects.get_or_create(username="admin")
        if created or not admin.check_password("admin"):
            admin.set_password("admin")
            admin.is_staff = True
            admin.save()

        accounts = {"user": user, "admin": admin}

        created_count = 0
        for data in TICKETS:
            owner = accounts[data["username"]]
            _, new = Ticket.objects.get_or_create(
                user=owner,
                title=data["title"],
                defaults={
                    "description": data["description"],
                    "severity": data["severity"],
                    "status": data["status"],
                },
            )
            if new:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created_count} ticket(s) created. "
                "Accounts: user/user (regular), admin/admin (staff)."
            )
        )
