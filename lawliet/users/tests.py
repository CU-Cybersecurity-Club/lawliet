import os
import random

from django.test import TestCase
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from uuid import UUID

from users.models import User

# Helper functions

from dashboard.tests.utils import *

"""
---------------------------------------------------
User tests (for custom User model)
---------------------------------------------------
"""


class UserTestCase(TestCase):
    def setUp(self):
        self.rd = random.Random()
        self.rd.seed(0)

        self.username, self.email, self.password = create_random_user(self.rd)

    def test_can_create_user(self):
        user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )

        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_can_create_superuser(self):
        user = User.objects.create_superuser(
            username=self.username, email=self.email, password=self.password
        )
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_username_with_illegal_characters(self):
        self.assertEqual(len(User.objects.all()), 0)

        for username in ("meepy@", "me^epy", "m(eep)y"):
            args = {
                "username": username,
                "email": self.email,
                "password": self.password,
            }
            self.assertRaises(ValidationError, lambda: User.objects.create_user(*args))
            self.assertEqual(len(User.objects.all()), 0)


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
