from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("tickets/<int:ticket_id>/delete/", views.delete_ticket_view, name="delete_ticket"),
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("tickets/<int:ticket_id>/close/", views.close_ticket_view, name="close_ticket"),
]
