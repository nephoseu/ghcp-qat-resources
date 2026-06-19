from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Ticket


def seed_users(sender, **kwargs):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_user(username="admin", password="admin", is_staff=True)
    if not User.objects.filter(username="user").exists():
        User.objects.create_user(username="user", password="user")


def authenticate_user(request, username: str, password: str):
    return django_authenticate(request, username=username, password=password)


def get_user_tickets(user: User):
    return Ticket.objects.filter(user=user).order_by("-created_at")


def get_all_tickets():
    return Ticket.objects.select_related("user").order_by("-created_at")


def create_ticket(user: User, title: str, description: str) -> Ticket:
    return Ticket.objects.create(user=user, title=title, description=description)


def delete_ticket(ticket_id: int, user: User) -> None:
    ticket = get_object_or_404(Ticket, id=ticket_id, user=user)
    ticket.delete()


def close_ticket(ticket_id: int) -> Ticket:
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.status = "closed"
    ticket.save()
    return ticket
