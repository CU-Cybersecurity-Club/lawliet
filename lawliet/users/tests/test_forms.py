"""
Tests for auth-related forms.
"""

from django.test import tag

from lawliet.test_utils import UnitTest, random_email, random_username, random_password
from users.forms import LoginForm, SignupForm
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
