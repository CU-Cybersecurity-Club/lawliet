from django import forms
from users.models import Profile
from dashboard.forms.fields import Textarea

"""
---------------------------------------------------
Profile
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
