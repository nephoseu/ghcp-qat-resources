from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from .api import authenticate_user, close_ticket, create_ticket, delete_ticket, get_all_tickets, get_user_tickets
from .forms import LoginForm, TicketForm

_staff_required = user_passes_test(lambda u: u.is_staff, login_url="/")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("admin_dashboard" if request.user.is_staff else "dashboard")

    form = LoginForm()
    error = None

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate_user(request, form.cleaned_data["username"], form.cleaned_data["password"])
            if user:
                login(request, user)
                return redirect("admin_dashboard" if user.is_staff else "dashboard")
            else:
                error = "Invalid username or password"

    return render(request, "tickets/login.html", {"form": form, "error": error})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")

    form = TicketForm()

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            create_ticket(request.user, form.cleaned_data["title"], form.cleaned_data["description"], form.cleaned_data["severity"])
            return redirect("dashboard")

    return render(request, "tickets/dashboard.html", {"form": form, "tickets": get_user_tickets(request.user)})


@login_required
def delete_ticket_view(request, ticket_id):
    if request.method == "POST":
        delete_ticket(ticket_id, request.user)
    return redirect("dashboard")


@login_required
@_staff_required
def admin_dashboard_view(request):
    return render(request, "tickets/admin_dashboard.html", {"tickets": get_all_tickets()})


@login_required
@_staff_required
def close_ticket_view(request, ticket_id):
    if request.method == "POST":
        close_ticket(ticket_id)
    return redirect("admin_dashboard")
