import os
import random

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from uuid import UUID

# Helper functions

random_username = lambda rd: f"meepy-{UUID(int=rd.getrandbits(128)).hex[:10]}"
random_email = lambda rd: f"meepy-{UUID(int=rd.getrandbits(128)).hex[:10]}@colorado.edu"
random_password = lambda rd: UUID(int=rd.getrandbits(128)).hex


"""
---------------------------------------------------
Profile tests
---------------------------------------------------
"""


class ProfileTestCase(TestCase):
    def setUp(self):
        # New users should use the default profile image
        path = settings.DEFAULT_PROFILE_IMAGE
        filename = path.split(os.sep)[-1]
        with open(path, "rb") as img:
            self.profile_image = SimpleUploadedFile(
                name=filename, content=img.read(), content_type="image/png"
            )

        # Set RNG for reproducible results
        self.rd = random.Random()
        self.rd.seed(0)

        self.email = random_email(self.rd)
        self.username = random_username(self.rd)
        self.password = random_password(self.rd)

        self.user = User.objects.create(
            username=self.username, email=self.email, password=self.password
        )

    def test_can_create_profile(self):
        user = User.objects.get(username=self.username)
        profile_image = user.profile.profile_image
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.profile.max_instances, settings.DEFAULT_MAX_INSTANCES)
        self.assertEqual(user.profile.active_instances, 0)
        self.assertTrue(profile_image.name.startswith(os.path.join("profiles", "img")))

        with open(settings.DEFAULT_PROFILE_IMAGE, "rb") as f:
            img = f.read()
            self.assertEqual(img, profile_image.read())
