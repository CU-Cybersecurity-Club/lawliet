import os

from django.test import Client, tag
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user
from uuid import UUID

from users.models import User

# Helper functions

from lawliet.test_utils import UnitTest

"""
---------------------------------------------------
User tests (for custom User model)
---------------------------------------------------
"""


@tag("auth", "users")
class UserTestCase(UnitTest):
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

    @tag("admin")
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

    def test_can_disable_user(self):
        """Should be able to disable users so that we can stop login."""
        user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )
        self.assertTrue(user.is_active)

        # Should be able to login as the user
        client = Client()
        client.login(username=self.username, password=self.password)
        self.assertTrue(get_user(client).is_authenticated)

        # Deactivate the user. Open session should be closed, and it should
        # be impossible to login as the disabled user.
        user.is_active = False
        user.save()

        self.assertFalse(get_user(client).is_authenticated)
        client.logout()

        client.login(username=self.username, password=self.password)
        self.assertFalse(get_user(client).is_authenticated)
