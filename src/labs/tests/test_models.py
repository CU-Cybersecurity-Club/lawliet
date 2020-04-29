import os

from django.test import tag
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from labs.models import LabEnvironment
from labs.forms import LabUploadForm
from lawliet.test_utils import UnitTest, random_docker_image

BASE_DIR = settings.BASE_DIR

STATIC_IMG_PATH = os.path.join(BASE_DIR, "assets", "img")
STATIC_IMG_PATH = os.path.abspath(STATIC_IMG_PATH)

"""
---------------------------------------------------
LabEnvironment tests
---------------------------------------------------
"""


@tag("labs")
class LabEnvironmentTestCase(UnitTest):
    def setUp(self):
        super().setUp()

        with open(os.path.join(STATIC_IMG_PATH, "meepy.png"), "rb") as img:
            self.cutter_image = SimpleUploadedFile(
                name="cutter.png", content=img.read(), content_type="image/png"
            )

        labenv = LabEnvironment.objects.create(
            name="Cutter + Radare2",
            description="Cutter & Radare2 desktop",
            url=random_docker_image(self.rd),
            protocol="vnc",
            port=5901,
        )

    def test_can_retrieve_basic_environment(self):
        """
        Retrieve the environment created in the setUp stage and test whether the
        environment was constructed correctly.
        """
        cutter_lab = LabEnvironment.objects.get(name="Cutter + Radare2")
        self.assertEqual(cutter_lab.description, "Cutter & Radare2 desktop")
