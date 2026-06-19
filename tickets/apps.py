from django.apps import AppConfig


class TicketsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tickets"

    def ready(self):
        from django.db.models.signals import post_migrate
        from .api import seed_users
        post_migrate.connect(seed_users, sender=self)
