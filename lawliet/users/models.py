import os

from django import forms
from django.db import models
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone
from django.utils.translation import gettext as _

from .managers import UserManager

"""
Settings for the User and models
"""
"""User options"""
MAX_EMAIL_ADDRESS_LENGTH = 150

MAX_USERNAME_LENGTH = 20
MIN_USERNAME_LENGTH = 3

MAX_PASSWORD_LENGTH = settings.MAX_PASSWORD_LENGTH
MIN_PASSWORD_LENGTH = settings.MIN_PASSWORD_LENGTH

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

    # Information about running labs
    n_active_labs = models.PositiveSmallIntegerField(default=0)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self):
        return self.username


"""
---------------------------------------------------
Admin forms for adding new users.
---------------------------------------------------
"""


class AddUserForm(forms.ModelForm):
    """
    A ModelForm based off of the custom User model for manually adding new users
    to the site.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(self.field_order)

    repassword = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}),
        label="Enter password again",
    )

    """
    Fields derived from the User model.
    """

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "repassword",
            "is_staff",
            "is_superuser",
        ]

        widgets = {
            "email": forms.TextInput(attrs={"placeholder": "Email address"}),
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "password": forms.PasswordInput(attrs={"placeholder": "Enter password"}),
        }

        labels = {"is_staff": "Add as staff member", "is_superuser": "Add as superuser"}

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        repassword = cleaned_data.get("repassword")

        if password != repassword:
            error = forms.ValidationError(
                _("The passwords you've entered don't match. Please try again."),
                code="invalid_signup",
            )
            self.add_error("repassword", error)

        return cleaned_data


"""
---------------------------------------------------
ModelAdmin child class to register the custom user model in the admin interface.
---------------------------------------------------
"""


class UserAdmin(admin.ModelAdmin):
    form = AddUserForm
