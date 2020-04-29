"""
Forms for handling labs (creation, deletion, etc.)
"""

from django import forms
from django.contrib import admin
from django.utils.translation import gettext as _

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
        fields = ["name", "description", "url", "protocol", "category"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Environment name",
                    "class": "uk-input uk-form-width-large",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    # "data-uk-htmleditor": "{markdown:true}",
                    "placeholder": "Add a description of the lab environment",
                    "class": "uk-textarea uk-form-width-large",
                }
            ),
            "category": forms.Select(
                choices=[
                    (_, _)
                    for _ in ("Reverse engineering", "Recon", "Web", "Miscellaneous",)
                ]
            ),
            "url": forms.TextInput(
                attrs={
                    "placeholder": "ex. wshand/cutter:latest",
                    "class": "uk-input uk-form-width-large",
                },
            ),
            "protocol": forms.Select(
                choices=[
                    (protocol.lower(), protocol) for protocol in ("SSH", "VNC", "RDP")
                ]
            ),
        }

        labels = {
            "url": "Docker image URL",
        }

        help_texts = {
            "protocol": (
                "Choose the protocol that Guacamole will use to connect "
                "to the container."
            )
        }

    def clean(self):
        cleaned_data = super().clean()

        # Add a port if one wasn't specified
        if "port" not in cleaned_data:
            protocol = cleaned_data.get("protocol")
            if protocol == "ssh":
                cleaned_data["port"] = 22
            elif protocol == "vnc":
                cleaned_data["port"] = 5901
            elif protocol == "rdp":
                cleaned_data["port"] = 3389
            else:
                error = forms.ValidationError(
                    _("The protocol must be SSH, VNC, or RDP."), code="bad_protocol",
                )
                self.add_error("protocol", error)

        print(f"CLEANED_DATA: {cleaned_data}")
        return cleaned_data


class LabEnvironmentAdmin(admin.ModelAdmin):
    form = LabUploadForm
