"""
Forms for changing user settings.
"""

from django import forms
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _

from users.models import User

MAX_PASSWORD_LENGTH = settings.MAX_PASSWORD_LENGTH
MIN_PASSWORD_LENGTH = settings.MIN_PASSWORD_LENGTH

"""
---------------------------------------------------
PasswordChangeForm
---------------------------------------------------
"""


class PasswordChangeForm(forms.Form):

    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter current password"}),
        help_text="Enter the current password you use to login to this account.",
        min_length=MIN_PASSWORD_LENGTH,
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter new password"}),
        help_text="Enter the new password you want to use.",
        validators=User.password.field.validators,
        min_length=MIN_PASSWORD_LENGTH,
    )

    new_repassword = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter new password again"}),
        help_text="Re-enter the new password you want to use.",
        min_length=MIN_PASSWORD_LENGTH,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()

        if len(self.errors) > 0:
            return cleaned_data

        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        new_repassword = cleaned_data.get("new_repassword")

        # Check whether old_password is the user's current password
        if not self.user.check_password(old_password):
            error = forms.ValidationError(_("The password you entered was incorrect."))
            self.add_error("old_password", error)
            return cleaned_data

        # Check whether the two entered passwords don't match up
        if new_password != new_repassword:
            error = forms.ValidationError(
                _("The new passwords you've entered don't match. Please try again.")
            )
            self.add_error("new_repassword", error)

        try:
            validate_password(new_password)
        except forms.ValidationError as error:
            self.add_error("new_password", error)
            return cleaned_data

        return cleaned_data
