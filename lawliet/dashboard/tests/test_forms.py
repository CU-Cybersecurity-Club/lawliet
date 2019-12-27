import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import tag
from dashboard.forms.auth import LoginForm, SignupForm
from dashboard.forms.settings import PasswordChangeForm
from dashboard.forms.labs import LabUploadForm
from uuid import UUID

from testing.base import UnitTest
from testing.utils import *

from labs.models import LabEnvironment
from users.models import User

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

        # Try a couple of invalid logins
        login_form = LoginForm(
            data={"username": self.username, "password": random_password(self.rd)}
        )
        self.assertFalse(login_form.is_valid())

        login_form = LoginForm(
            data={"username": random_username(self.rd), "password": self.password}
        )
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


"""
---------------------------------------------------
LabUploadForm tests
---------------------------------------------------
"""


@tag("forms", "labs")
class LabUploadFormTestCase(UnitTest):
    def setUp(self):
        super().setUp(create_user=True)

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

    @tag("admin", "auth")
    def test_nonstaff_no_upload_lab(self):
        """
        Non-staff users shouldn't be able to upload new labs.
        """
        username, email, password = create_random_user(self.rd)
        user = User.objects.create_user(
            username=username, email=email, password=password, is_staff=False
        )
        self.fail("TODO")
