"""
Forms to provide authentication functionality.
"""

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from .fields import PasswordField, UsernameField, EmailField

MAX_EMAIL_ADDRESS_LENGTH = settings.MAX_EMAIL_ADDRESS_LENGTH
MAX_USERNAME_LENGTH = settings.MAX_USERNAME_LENGTH
MIN_USERNAME_LENGTH = settings.MIN_USERNAME_LENGTH
MAX_PASSWORD_LENGTH = settings.MAX_PASSWORD_LENGTH
MIN_PASSWORD_LENGTH = settings.MIN_PASSWORD_LENGTH

"""
---------------------------------------------------
SignupForm
---------------------------------------------------
"""


class SignupForm(forms.Form):
    """
    Form fields
    """

    email = EmailField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter email"}
        ),
        help_text=(
            "Enter email. Your email address must be less than "
            f"{MAX_EMAIL_ADDRESS_LENGTH} characters long."
        ),
        max_length=MAX_EMAIL_ADDRESS_LENGTH,
    )

    username = UsernameField(
        placeholder="Select a username",
        help_text=(
            f"Select a username. Your username must be {MIN_USERNAME_LENGTH}-"
            f"{MAX_USERNAME_LENGTH} characters long, and may only contain "
            "letters, numbers, periods (.),  dashes (-), and underscores (_)."
        ),
    )

    password = PasswordField(
        placeholder="Enter password",
        help_text=(
            f"Enter password. Must be {MIN_PASSWORD_LENGTH}-"
            f"{MAX_PASSWORD_LENGTH} characters long."
        ),
    )

    repassword = PasswordField(
        placeholder="Enter password again", help_text="Enter password again.", label=""
    )

    """
    Form validation
    """

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("The email address '%(email)s' has already been registered."),
                params={"email": email},
                code="exists",
            )

        # Need to avoid workarounds where an email matches a username already in
        # the database, which could lead to unexpected bugs (e.g. if we decide to
        # allow authentication with either username or email.)
        if User.objects.filter(username=email).exists():
            # TODO: better error message / code?
            raise forms.ValidationError(
                _("Invalid email address."), code="username_email_matchup"
            )

        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                _("Sorry, the username '%(username)s' has already been taken."),
                params={"username": username},
                code="exists",
            )

        # TODO: check that username matches regex

        # Need to avoid workarounds where a username matches an email already in
        # the database, which could lead to unexpected bugs (e.g. if we decide to
        # allow authentication with either username or email.)
        if User.objects.filter(email=username).exists():
            # TODO: better error message / code?
            raise forms.ValidationError(
                _("Invalid username."), code="username_email_matchup"
            )

        return username

    def clean(self):
        cleaned_data = super().clean()

        # Validate password and re-entered password
        password = cleaned_data.get("password")
        repassword = cleaned_data.get("repassword")

        if password != repassword:
            error = forms.ValidationError(
                _("The passwords you've entered don't match. Please try again."),
                code="invalid_login",
            )
            self.add_error("repassword", error)

        return cleaned_data


"""
---------------------------------------------------
LoginForm
---------------------------------------------------
"""


class LoginForm(forms.Form):
    """
    Form fields
    """

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        ),
        help_text="Enter the username you registered with.",
        max_length=settings.MAX_USERNAME_LENGTH,
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
        help_text="Enter the password you used to sign up.",
        max_length=settings.MAX_PASSWORD_LENGTH,
    )

    remember_user = forms.BooleanField(
        help_text="Remember me", label="Remember me", required=False
    )

    """
    Form validation
    """

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                _("The username '%(username)s' could not be found."),
                params={"username": username},
                code="nonexistent",
            )

        user = authenticate(username=username, password=password)

        if not user:
            raise forms.ValidationError(
                _("Sorry, that login was invalid. Please try again."),
                code="invalid_login",
            )
        if not user.is_active:
            raise forms.ValidationError(
                _("This user's account is not currently active."),
                code="inactive_account",
            )

        return cleaned_data

    def login(self, request):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        remember = self.cleaned_data.get("remember_user")

        # TODO: change expiry in accordance with whether or not the 'remember'
        # option is set.

        user = authenticate(username=username, password=password)
        return user
