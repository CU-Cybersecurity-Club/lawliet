"""
Commonly used fields to plug into different forms
"""

from django import forms


class TextInput(forms.TextInput):
    """TextInput widget with custom styling."""

    def __init__(self, placeholder=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs = {"class": "form-control", "placeholder": placeholder}


class PasswordInput(forms.PasswordInput):
    """TextInput widget with custom styling."""

    def __init__(self, placeholder=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs = {"class": "form-control", "placeholder": placeholder}
