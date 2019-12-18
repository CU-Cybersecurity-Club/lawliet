"""
Commonly used fields to plug into different forms
"""

from django import forms
from django.conf import settings
from django.core.validators import RegexValidator


class PasswordField(forms.CharField):
    """
    Custom Field for entering passwords.
    """

    def __init__(
        self,
        placeholder="",
        max_length=settings.MAX_PASSWORD_LENGTH,
        min_length=settings.MIN_PASSWORD_LENGTH,
        *args,
        **kwargs
    ):

        super().__init__(*args, **kwargs)
        self.widget = forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": placeholder}
        )


class UsernameField(forms.CharField):
    """
    Custom Field for entering usernames.
    """

    def __init__(
        self,
        max_length=settings.MAX_USERNAME_LENGTH,
        min_length=settings.MIN_USERNAME_LENGTH,
        placeholder="",
        *args,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        # Add CSS styling to the <input>
        self.widget = forms.TextInput(
            attrs={"class": "form-control", "placeholder": placeholder}
        )

        # Restrict the characters allowed in the username
        self.validators = [
            RegexValidator(
                r"^[\w\.\-_]+$",
                (
                    "Your username may only contain letters, numbers, periods "
                    "(.), dashes (-), and underscores (_)."
                ),
            )
        ]


class EmailField(forms.EmailField):
    """
    Custom Field for entering emails.
    """

    def __init__(
        self,
        max_length=settings.MAX_EMAIL_ADDRESS_LENGTH,
        placeholder="",
        *args,
        **kwargs
    ):

        super().__init__(*args, **kwargs)
        self.widget = forms.TextInput(
            attrs={"class": "form-control", "placeholder": placeholder}
        )
