from django.contrib.auth.models import User
from django.db import models


class Ticket(models.Model):
    SEVERITY_CHOICES = [
        ("critical", "Critical"),
        ("high",     "High"),
        ("medium",   "Medium"),
        ("low",      "Low"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="medium")
    status = models.CharField(max_length=20, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
