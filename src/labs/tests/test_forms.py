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
            "protocol": "ssh",
        }
        form = LabUploadForm(data)
        self.assertTrue(form.is_valid())

        # Save the new environment to the database
        LabEnvironment.objects.create(**form.cleaned_data)
        # form.save()
        self.assertEqual(len(LabEnvironment.objects.all()), 1)

        lab = LabEnvironment.objects.get(name=self.lab_name)
        self.assertEqual(lab.description, self.lab_description)
        self.assertEqual(lab.url, self.lab_url)
