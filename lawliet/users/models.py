import os

from django.db import models
from django.conf import settings
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone

from .managers import UserManager

"""
Settings for the User and models
"""
"""User options"""
MAX_EMAIL_ADDRESS_LENGTH = 150
MAX_USERNAME_LENGTH = 20
MIN_USERNAME_LENGTH = 3

"""
---------------------------------------------------
Custom User model
---------------------------------------------------
"""


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                r"^[\w\.\-_]+$",
                (
                    "Your username may only contain letters, numbers, periods "
                    "(.), dashes (-), and underscores (_)."
                ),
            ),
            MinLengthValidator(MIN_USERNAME_LENGTH),
        ],
    )

    email = models.EmailField(max_length=MAX_EMAIL_ADDRESS_LENGTH, unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self):
        return self.username


class UserAdmin(ModelAdmin):
    pass
