"""
Custom widgets for use across the project.
"""

from django import forms

"""
---------------------------------------------------
Custom text input widgets
---------------------------------------------------
"""


class IconTextInput(forms.TextInput):
    """
    Modified TextInput widget that places a UIkit icon on the left side of the
    input field.
    """

    template_name = "widgets/icon_text.html"

    def get_context(self, *args):
        context = super().get_context(*args)

        # Add an icon_name field to the context so that we can insert an icon
        # into the text field.
        try:
            context["widget"].setdefault("icon_name", self.icon_name)
        except AttributeError:
            pass

        # Add a default placeholder for the field
        try:
            if "attrs" not in context["widget"]:
                context["widget"]["attrs"] = {}
            context["widget"]["attrs"].setdefault("placeholder", self.placeholder)
        except AttributeError:
            pass

        return context


### Subtypes of IconTextInput


class EmailTextInput(IconTextInput):
    icon_name = "mail"


class IconlessPasswordInput(IconTextInput):
    def get_context(self, *args):
        context = super().get_context(*args)
        context["widget"]["type"] = "password"
        return context


class PasswordInput(IconlessPasswordInput):
    icon_name = "lock"


class UsernameTextInput(IconTextInput):
    icon_name = "user"


class URLTextInput(IconTextInput):
    icon_name = "link"
