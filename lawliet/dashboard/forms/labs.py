"""
Forms for handling labs (creation, deletion, etc.)
"""

from django.forms import ModelForm
from dashboard.models import LabEnvironment
from dashboard.forms.fields import TextInput, Textarea

"""
---------------------------------------------------
LabUploadform
---------------------------------------------------
"""


class LabUploadForm(ModelForm):
    class Meta:
        model = LabEnvironment
        fields = ["name", "description", "url", "header_image"]
        widgets = {
            "name": TextInput(attrs={"placeholder": "Environment name"}),
            "description": Textarea(
                attrs={"placeholder": "Add a description of the lab environment"}
            ),
            "url": TextInput(
                attrs={"placeholder": "ex. https://hub.docker.com/r/wshand/cutter"}
            ),
        }
        labels = {"url": "Docker image URL"}
