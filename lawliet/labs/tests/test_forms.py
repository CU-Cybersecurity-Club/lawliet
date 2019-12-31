import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import tag

from labs.forms import LabUploadForm
from labs.models import LabEnvironment
from lawliet.test_utils import UnitTest

"""
---------------------------------------------------
LabUploadForm tests
---------------------------------------------------
"""


@tag("forms", "labs")
class LabUploadFormTestCase(UnitTest):
    """
        class LabUploadFormTestCase(lawliet.test_utils.UnitTest)

    Unit tests for labs.forms.LabUploadForm.
    """

    def setUp(self):
        super().setUp(create_user=True)
        self.user.is_staff = True
        self.user.save()

        # Lab params
        self.lab_url = "https://hub.docker.com/r/wshand/cutter:latest"
        self.lab_name = "Cutter"
        self.lab_description = "Cutter lab environment"
        self.lab_image_path = os.path.join(
            settings.BASE_DIR, "assets", "img", "meepy.png"
        )
        with open(self.lab_image_path, "rb") as img:
            filename = self.lab_image_path.split(os.sep)[-1]
            self.lab_image = SimpleUploadedFile(
                filename, img.read(), content_type="image/png"
            )

    def test_create_new_environment(self):
        """
        Use the LabUploadForm to create a new lab environment, and check
        that the environment was constructed correctly.
        """
        self.assertEqual(len(LabEnvironment.objects.all()), 0)
        data = {
            "name": self.lab_name,
            "description": self.lab_description,
            "url": self.lab_url,
            "has_web_interface": True,
        }
        file_data = {"header_image": self.lab_image}
        form = LabUploadForm(data, file_data)
        self.assertTrue(form.is_valid())

        # Save the new environment to the database
        form.save()
        self.assertEqual(len(LabEnvironment.objects.all()), 1)

        lab = LabEnvironment.objects.get(name=self.lab_name)
        self.assertEqual(lab.description, self.lab_description)
        self.assertEqual(lab.url, self.lab_url)
        self.assertTrue(lab.has_web_interface)
        with open(self.lab_image_path, "rb") as img:
            self.assertEqual(lab.header_image.read(), img.read())
