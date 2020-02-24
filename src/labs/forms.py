"""
Forms for handling labs (creation, deletion, etc.)
"""

from django import forms
from django.contrib import admin

from lawliet.widgets import URLTextInput
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
        fields = ["name", "description", "url", "has_web_interface"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Environment name",
                    "class": "uk-form-width-large",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    # "data-uk-htmleditor": "{markdown:true}",
                    "placeholder": "Add a description of the lab environment",
                    "class": "uk-form-width-large",
                }
            ),
            "url": URLTextInput(
                attrs={
                    "placeholder": "ex. https://hub.docker.com/r/wshand/cutter",
                    "class": "uk-form-width-large",
                }
            ),
            "has_web_interface": forms.CheckboxInput(),
        }

        labels = {
            "url": "Docker image URL",
            "has_web_interface": "HTTP web interface",
        }

        help_texts = {
            "has_web_interface": (
                "Check the box below if the lab environment you're adding has an "
                "HTTP web interface (i.e., it has an interface that can be accessed "
                "via port 80)."
            )
        }

        initial = {"has_web_interface": True}


class LabEnvironmentAdmin(admin.ModelAdmin):
    form = LabUploadForm
