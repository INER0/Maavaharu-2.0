from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model. One account table for every kind of person in the
    system; the `role` field decides what they are allowed to do."""

    class Role(models.TextChoices):
        VISITOR = 'visitor', 'Visitor'
        HOTEL_MANAGER = 'hotel_manager', 'Hotel Manager'
        FERRY_OPERATOR = 'ferry_operator', 'Ferry Operator'
        THEMEPARK_STAFF = 'themepark_staff', 'Theme Park Staff'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VISITOR,
    )
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
