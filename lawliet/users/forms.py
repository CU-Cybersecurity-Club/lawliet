from django.forms import ModelForm
from users.models import Profile

"""
---------------------------------------------------
Profile
---------------------------------------------------
"""


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_image", "description"]
