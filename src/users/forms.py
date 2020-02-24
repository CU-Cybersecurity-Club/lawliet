"""
Forms to provide authentication functionality.
"""

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _

from users.models import User, EmailVerificationToken

import users.models as umodels

MAX_EMAIL_ADDRESS_LENGTH = umodels.MAX_EMAIL_ADDRESS_LENGTH
MAX_USERNAME_LENGTH = umodels.MAX_USERNAME_LENGTH
MIN_USERNAME_LENGTH = umodels.MIN_USERNAME_LENGTH
MAX_PASSWORD_LENGTH = User.password.field.max_length
MIN_PASSWORD_LENGTH = settings.MIN_PASSWORD_LENGTH


"""
---------------------------------------------------
SignupForm
---------------------------------------------------
"""


class SignupForm(forms.ModelForm):
    """
    Form fields
    """

    repassword = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password again"}),
        label="",
        help_text="Re-enter the password you entered in the previous box.",
        max_length=User.password.field.max_length,
        min_length=MIN_PASSWORD_LENGTH,
    )

    class Meta:
        model = User

        fields = ("email", "username", "password")

        widgets = {
            "email": forms.TextInput(attrs={"placeholder": "Enter your email address"}),
            "username": forms.TextInput(attrs={"placeholder": "Select a username"}),
            "password": forms.PasswordInput(
                attrs={
                    "minlength": MIN_PASSWORD_LENGTH,
                    "placeholder": "Choose a password",
                }
            ),
        }

        help_texts = {
            "email": (
                "Enter email. Your email address must be less than "
                f"{MAX_EMAIL_ADDRESS_LENGTH} characters long."
            ),
            "username": (
                f"Select a username. Your username must be {MIN_USERNAME_LENGTH}-"
                f"{MAX_USERNAME_LENGTH} characters long, and may only contain "
                "letters, numbers, periods (.),  dashes (-), and underscores (_)."
            ),
            "password": (
                f"Enter password. Must be {MIN_PASSWORD_LENGTH}-"
                f"{MAX_PASSWORD_LENGTH} characters long."
            ),
        }

    """
    Form validation
    """

    def clean(self):
        cleaned_data = super().clean()

        # Validate password and re-entered password
        password = cleaned_data.get("password")
        repassword = cleaned_data.get("repassword")

        try:
            validate_password(password)
        except forms.ValidationError as error:
            self.add_error("password", error)
            return cleaned_data

        if password != repassword:
            error = forms.ValidationError(
                _("The passwords you've entered don't match. Please try again."),
                code="invalid_login",
            )
            self.add_error("password", error)

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
        widget=forms.TextInput(attrs={"placeholder": "Username"}),
        help_text="Enter the username you registered with.",
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
        help_text="Enter the password you used to sign up.",
        min_length=MIN_PASSWORD_LENGTH,
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
                _("The user with username '%(username)s' could not be found."),
                params={"username": username},
                code="nonexistent",
            )

        user = User.objects.get(username=username)
        if not user.is_active:
            # If there's an email verification token out on the user, then
            # they can't sign up until they've verified their email address.
            if EmailVerificationToken.objects.filter(username=username).exists():
                raise forms.ValidationError(
                    _("You must verify your email address before you can login."),
                    code="inactive_account",
                )
            else:
                raise forms.ValidationError(
                    _("This user's account is currently deactivated."),
                    code="inactive_account",
                )

        user = authenticate(username=username, password=password)

        if not user:
            raise forms.ValidationError(
                _("Sorry, that login was invalid. Please try again."),
                code="invalid_login",
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
