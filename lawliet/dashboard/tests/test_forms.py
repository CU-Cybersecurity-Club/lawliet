import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import tag
from dashboard.forms.auth import LoginForm, SignupForm
from dashboard.forms.settings import PasswordChangeForm
from uuid import UUID

from lawliet.test_utils import *

from labs.models import LabEnvironment
from users.models import User, EmailVerificationToken

"""
---------------------------------------------------
SignupForm tests
---------------------------------------------------
"""


@tag("auth", "forms")
class SignupFormTestCase(UnitTest):
    def setUp(self):
        super().setUp()
        self.form_data = {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "repassword": self.password,
        }

    def test_signup(self):
        """
        Submit some valid data to the SignUp form, and ensure that the
        form validates it.
        """
        signup_form = SignupForm(data=self.form_data)
        self.assertTrue(signup_form.is_valid())

    def test_cannot_sign_up_existing_username_or_email(self):
        """
        Users should be unable to sign up with a username or email that's
        already been registered.
        """
        signup_form = SignupForm(data=self.form_data)
        self.assertTrue(signup_form.is_valid())

        User.objects.create_user(
            username=self.username, password=self.password, email=self.email
        )

        # Can't sign up same username twice
        signup_form = SignupForm(
            data={
                "username": self.username,
                "email": random_email(self.rd),
                "password": self.password,
                "repassword": self.password,
            }
        )
        self.assertFalse(signup_form.is_valid())

        # Can't sign up same email twice
        signup_form = SignupForm(
            data={
                "username": random_username(self.rd),
                "email": self.email,
                "password": self.password,
                "repassword": self.password,
            }
        )
        self.assertFalse(signup_form.is_valid())

    def test_password_and_repassword_must_match(self):
        """
        In the signup form, the two passwords that the user enters
        must match with one another.
        """
        signup_form = SignupForm(
            data={
                "username": self.username,
                "email": self.email,
                "password": random_password(self.rd),
                "repassword": random_password(self.rd),
            }
        )
        self.assertFalse(signup_form.is_valid())

    def test_sign_up_with_invalid_password(self):
        """
        Ensure that the SignupForm enforces the correct restrictions on
        passwords.
        """
        # Test: passwords must meet the minimum password length
        signup_form = SignupForm(
            data={
                "username": self.username,
                "email": self.email,
                "password": self.password[:6],
                "repassword": self.password[:6],
            }
        )
        self.assertFalse(signup_form.is_valid())

        # Test: passwords must not be too common
        signup_form = SignupForm(
            data={
                "username": self.username,
                "email": self.email,
                "password": "password",
                "repassword": "password",
            }
        )
        self.assertFalse(signup_form.is_valid())


"""
---------------------------------------------------
LoginForm tests
---------------------------------------------------
"""


@tag("auth", "forms")
class LoginFormTestCase(UnitTest):
    def setUp(self):
        super().setUp(create_user=True)
        self.form_data = {"username": self.username, "password": self.password}

    def test_login(self):
        user = User.objects.get(username=self.username)
        login_form = LoginForm(data=self.form_data)
        login_form.is_valid()
        self.assertTrue(login_form.is_valid())

    def test_invalid_login(self):
        # Try a couple of invalid logins
        login_form = LoginForm(
            data={"username": self.username, "password": random_password(self.rd)}
        )
        self.assertFalse(login_form.is_valid())

        login_form = LoginForm(
            data={"username": random_username(self.rd), "password": self.password}
        )
        self.assertFalse(login_form.is_valid())

    def test_login_with_deactivated_account(self):
        """Attempt to log in as a deactivated user."""
        user = User.objects.get(username=self.username)
        user.is_active = False
        user.save()
        login_form = LoginForm(data=self.form_data)
        self.assertFalse(login_form.is_valid())


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
