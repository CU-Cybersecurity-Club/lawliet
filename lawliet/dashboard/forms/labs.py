"""
Forms for handling labs (creation, deletion, etc.)
"""

from django.forms import ModelForm
from dashboard.models import LabEnvironment


class LabCreationForm(ModelForm):
    class Meta:
        model = LabEnvironment
        fields = ["name", "description", "header_image"]
