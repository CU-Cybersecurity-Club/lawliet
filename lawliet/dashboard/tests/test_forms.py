import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import tag
from dashboard.forms.settings import PasswordChangeForm
from uuid import UUID

from lawliet.test_utils import *

from labs.models import LabEnvironment
from users.models import User, EmailVerificationToken

"""
---------------------------------------------------
PasswordChangeForm tests
---------------------------------------------------
"""


@tag("auth", "forms", "user-settings")
class PasswordChangeFormTests(UnitTest):
    def setUp(self):
        super().setUp(create_user=True)

    def test_valid_password_change(self):
        # Login as the user and attempt to submit a
        # password change request through the form.
        new_password = random_password(self.rd)
        form = PasswordChangeForm(
            self.user,
            data={
                "old_password": self.password,
                "new_password": new_password,
                "new_repassword": new_password,
            },
        )
        self.assertTrue(form.is_valid())

    def test_invalid_password_change(self):
        # Input data should fail to be validated in the following
        # cases:
        # - The old_password isn't the user's password
        # - The new password fields don't match up
        new_password = random_password(self.rd)
        form = PasswordChangeForm(
            self.user,
            data={
                "old_password": random_password(self.rd),
                "new_password": new_password,
                "new_repassword": new_password,
            },
        )
        self.assertFalse(form.is_valid())

        form = PasswordChangeForm(
            self.user,
            data={
                "old_password": self.password,
                "new_password": random_password(self.rd),
                "new_repassword": random_password(self.rd),
            },
        )
        self.assertFalse(form.is_valid())
