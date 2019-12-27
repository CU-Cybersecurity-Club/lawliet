from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.models import Profile
from dashboard.forms.fields import Textarea

"""
---------------------------------------------------
User profile modification
---------------------------------------------------
"""


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_image", "description"]
        widgets = {
            "profile_image": forms.ClearableFileInput(),
            "description": Textarea(attrs={"placeholder": "Describe yourself here"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("profile_image")

        if self.errors:
            return cleaned_data

        if image is None:
            # Keep the user's current profile image
            image = self.instance.profile.profile_image
            cleaned_data["profile_image"] = image

        return cleaned_data
