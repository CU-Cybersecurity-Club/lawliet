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
            header_image=self.cutter_image,
        )

    def test_can_retrieve_basic_environment(self):
        """
        Retrieve the environment created in the setUp stage and test whether the
        environment was constructed correctly.
        """
        cutter_lab = LabEnvironment.objects.get(name="Cutter + Radare2")
        path = cutter_lab.header_image.path
        self.assertEqual(cutter_lab.description, "Cutter & Radare2 desktop")
        self.assertTrue(path.startswith(settings.MEDIA_ROOT))
        self.assertTrue(
            path.startswith(os.path.join(settings.MEDIA_ROOT, "labs", "img"))
        )
        self.assertTrue(cutter_lab.has_web_interface)  # True by default


"""
---------------------------------------------------
LabUploadForm tests
---------------------------------------------------
"""


@tag("forms", "labs")
class LabUploadFormTestCase(UnitTest):
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
