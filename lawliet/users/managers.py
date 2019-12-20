from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext as _
from django.core.validators import RegexValidator

"""
---------------------------------------------------
UserManager object for the custom User model
---------------------------------------------------
"""


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)

        # Validate the User instance's fields, and save the User
        # to the database.
        result = user.full_clean()
        user.save()

        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser must be created with is_staff=True."))
        elif not extra_fields.get("is_superuser"):
            raise ValueError(_("Superuser must be created with is_superuser=True."))
        else:
            return self.create_user(
                username=username, email=email, password=password, **extra_fields
            )
