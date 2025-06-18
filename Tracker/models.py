# Tracker/models.py
from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  
    category = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)

ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('custom_admin', 'Custom Admin'),
    ('team_member', 'Team Member'),
    ('finance_officer', 'Finance Officer'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='team_member')

    def __str__(self):
        return f"{self.user.username} - {self.role}"