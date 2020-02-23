"""
Forms for handling labs (creation, deletion, etc.)
"""

from django import forms
from django.contrib import admin

from lawliet.fields import TextInput, Textarea
from labs.models import LabEnvironment

"""
---------------------------------------------------
LabUploadform
---------------------------------------------------
"""


class LabUploadForm(forms.ModelForm):
    """
    A ModelForm based off the LabEnvironment model for uploading new environments
    to Lawliet.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = LabEnvironment
        fields = ["name", "description", "url", "header_image", "has_web_interface"]
        widgets = {
            "name": TextInput(attrs={"placeholder": "Environment name",}),
            "description": Textarea(
                attrs={
                    "data-uk-htmleditor": "{markdown:true}",
                    "placeholder": "Add a description of the lab environment",
                }
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


class LabEnvironmentAdmin(admin.ModelAdmin):
    form = LabUploadForm
