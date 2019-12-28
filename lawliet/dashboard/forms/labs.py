"""
Forms for handling labs (creation, deletion, etc.)
"""

from django import forms
from django.forms import ModelForm

from testing.fields import TextInput, Textarea
from labs.models import LabEnvironment

"""
---------------------------------------------------
LabUploadform
---------------------------------------------------
"""


class LabUploadForm(ModelForm):
    """
    A ModelForm based off the LabEnvironment model for uploading new environments
    to Lawliet.
    """

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = LabEnvironment
        fields = ["name", "description", "url", "header_image", "has_web_interface"]
        widgets = {
            "name": TextInput(attrs={"placeholder": "Environment name"}),
            "description": Textarea(
                attrs={"placeholder": "Add a description of the lab environment"}
            ),
            "url": TextInput(
                attrs={"placeholder": "ex. https://hub.docker.com/r/wshand/cutter"}
            ),
            "has_web_interface": forms.CheckboxInput(
                attrs={"class": "boolean-selection"}
            ),
        }

        labels = {
            "url": "Docker image URL",
            "has_web_interface": "Has HTTP web interface",
        }

        initial = {"has_web_interface": True}

    def clean(self):
        cleaned_data = super().clean()

        if not self.user.is_staff:
            raise forms.ValidationError(
                "Only staff members are allowed to upload new labs."
            )

        return cleaned_data
