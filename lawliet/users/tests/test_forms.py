import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import tag
from users.forms import ProfileForm

from testing.base import UnitTest

"""
---------------------------------------------------
ProfileForm tests
---------------------------------------------------
"""


@tag("forms", "profile", "users")
class ProfileFormTestCase(UnitTest):
    def setUp(self):
        super().setUp(create_user=True)

        img_path = os.path.join("assets", "svg", "ikonate", "happy-face.svg")
        with open(img_path, "rb") as img:
            self.new_profile_img = SimpleUploadedFile(
                name="happy-face.svg", content=img.read(), content_type="img/svg"
            )

    def test_change_user_profile_information(self):
        """
        Submit valid data through the ProfileForm, and ensure that it was
        validated by the form.
        """
        form_data = {
            "profile_image": self.new_profile_img,
            "description": "Hi! I'm Meepy!",
        }
        profile_form = ProfileForm(instance=self.user, data=form_data)
        self.assertTrue(profile_form.is_valid())
