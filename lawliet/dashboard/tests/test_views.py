"""
Tests for the views offered by the dashboard app.
"""
import os

from django.test import tag
from django.conf import settings
from django.urls import reverse

from users.models import User
from lawliet.test_utils import *

"""
---------------------------------------------------
Global variables
---------------------------------------------------
"""


MIN_PASSWORD_LENGTH = settings.MIN_PASSWORD_LENGTH

"""
---------------------------------------------------
Settings tests
---------------------------------------------------
"""


@tag("user-settings", "views")
class SettingsViewTestCase(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)

        # Form data for resetting password
        self.new_password = random_password(self.rd)
        self.newpass_data = {
            "old_password": self.password,
            "new_password": self.new_password,
            "new_repassword": self.new_password,
            "password-change-submit-button": "",
        }

    def test_user_settings_template(self):
        response = self.client.get(reverse("user settings"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(
            response, os.path.join("dashboard", "dashboard_base.html")
        )
        self.assertTemplateUsed(
            response, os.path.join("dashboard", "user_settings.html")
        )

    @tag("user")
    def test_change_password(self):
        response = self.client.post(reverse("user settings"), self.newpass_data)
        user = User.objects.get(username=self.username)
        self.assertFalse(user.check_password(self.password))
        self.assertTrue(user.check_password(self.new_password))

    @tag("user")
    def test_change_password_with_incorrect_old_password(self):
        """Attempt to change password with an invalid old password."""
        self.newpass_data["old_password"] = random_password(self.rd)
        initial_pass = self.user.password
        response = self.client.post(reverse("user settings"), self.newpass_data)

        user = User.objects.get(username=self.username)
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.check_password(self.new_password))
        self.assertFormError(
            response,
            "password_change_form",
            "old_password",
            "The password you entered was incorrect.",
        )

    @tag("user")
    def test_change_password_with_nonmatching_repassword(self):
        """Attempt to change password with nonmatching new passwords."""
        self.newpass_data["new_repassword"] = random_password(self.rd)
        response = self.client.post(reverse("user settings"), self.newpass_data)
        user = User.objects.get(username=self.username)
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.check_password(self.new_password))
        self.assertFormError(
            response,
            "password_change_form",
            "new_repassword",
            "The new passwords you've entered don't match. Please try again.",
        )

    @tag("user")
    def test_change_password_with_invalid_password(self):
        """
        Attempt to change the user's password to a password that fails
        the password validators.
        """
        initial_pass = self.user.password

        # Password length is too short
        new_password = random_password(self.rd)[:6]
        self.newpass_data["new_password"] = new_password
        self.newpass_data["new_repassword"] = new_password
        response = self.client.post(reverse("user settings"), self.newpass_data)
        self.assertEqual(self.user.password, initial_pass)
        self.assertFormError(
            response,
            "password_change_form",
            "new_password",
            f"Ensure this value has at least {MIN_PASSWORD_LENGTH} characters (it has {len(new_password)}).",
        )
        self.assertFormError(
            response,
            "password_change_form",
            "new_repassword",
            f"Ensure this value has at least {MIN_PASSWORD_LENGTH} characters (it has {len(new_password)}).",
        )

        # Password is too common
        self.newpass_data["new_password"] = "password"
        self.newpass_data["new_repassword"] = "password"
        response = self.client.post(reverse("user settings"), self.newpass_data)
        self.assertEqual(self.user.password, initial_pass)
        self.assertFormError(
            response,
            "password_change_form",
            "new_password",
            "This password is too common.",
        )


"""
---------------------------------------------------
Lab tests
---------------------------------------------------
"""


@tag("views", "labs")
class LabUploadTestCase(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)

    def test_lab_upload_restricted_to_staff(self):
        # If a non-staff member tries to visit the upload form, they should
        # be automatically redirected to the dashboard.
        response = self.client.get(reverse("upload lab"), follow=True)
        location, status_code = response.redirect_chain[-1]
        self.assertEqual(location, reverse("dashboard"))

        # Staff users should be able to visit the upload form
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse("upload lab"), follow=True)
        self.assertEqual(response.status_code, 200)
