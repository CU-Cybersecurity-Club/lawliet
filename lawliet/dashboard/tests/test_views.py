"""
Tests for the views offered by the dashboard app.
"""
import os

from django.test import tag
from django.conf import settings
from django.contrib.auth import get_user, login, logout
from django.urls import reverse
from uuid import UUID

from testing.base import UnitTest
from testing.utils import *
from users.models import User

"""
---------------------------------------------------
Signup tests
---------------------------------------------------
"""

MIN_PASSWORD_LENGTH = settings.MIN_PASSWORD_LENGTH

"""
---------------------------------------------------
Signup tests
---------------------------------------------------
"""


@tag("auth", "views")
class SignupViewTestCase(UnitTest):
    def setUp(self):
        super().setUp()
        self.form_data = signup_form_data(self.username, self.email, self.password)

    def test_signup(self):
        """
        Create a new user and check that they were registered in the database.
        """
        response = self.client.get(reverse("signup"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, os.path.join("dashboard", "signup.html"))

        response = self.client.post(reverse("signup"), self.form_data)

        user = User.objects.get(username=self.username)
        self.assertEqual(len(User.objects.all()), 1)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

    def test_signup_as_registered_email_or_user(self):
        """
        Attempt to sign up as new user with registered email address or username.
        """
        # Start by adding a new user to the database
        user = User.objects.create_user(
            email=self.email, username=self.username, password=self.password
        )

        # Attempt to sign up a user with the same email
        form_data = random_signup_form(self.rd)
        form_data["email"] = self.email
        response = self.client.post(reverse("signup"), form_data)

        self.assertEqual(len(User.objects.all()), 1)
        self.assertEqual(user, User.objects.get(email=self.email))
        self.assertFormError(
            response, "form", "email", "User with this Email already exists."
        )

        # Attempt to sign up a user with the same username
        form_data = random_signup_form(self.rd)
        form_data["username"] = self.username
        response = self.client.post(reverse("signup"), form_data)

        self.assertEqual(len(User.objects.all()), 1)
        self.assertEqual(user, User.objects.get(username=self.username))
        self.assertFormError(
            response, "form", "username", "User with this Username already exists."
        )

    def test_sign_up_with_nonmatching_passwords(self):
        """
        Attempt to sign up with different data in the two password fields.
        """
        self.form_data["repassword"] = random_password(self.rd)
        response = self.client.post(reverse("signup"), self.form_data)
        self.assertEqual(len(User.objects.all()), 0)
        self.assertFormError(
            response,
            "form",
            "password",
            "The passwords you've entered don't match. Please try again.",
        )

    def test_sign_up_with_invalid_password(self):
        """
        Attempt to sign up with passwords that fail to pass the validators.
        """
        # Try to sign up with a password that's too short
        self.form_data["password"] = self.password[:6]
        self.form_data["repassword"] = self.password[:6]
        response = self.client.post(reverse("signup"), self.form_data)
        self.assertEqual(len(User.objects.all()), 0)
        self.assertFormError(
            response,
            "form",
            "password",
            f"This password is too short. It must contain at least {MIN_PASSWORD_LENGTH} characters.",
        )

        # Try to sign up with a password that's too common
        self.form_data["password"] = "password"
        self.form_data["repassword"] = "password"
        response = self.client.post(reverse("signup"), self.form_data)
        self.assertEqual(len(User.objects.all()), 0)
        self.assertFormError(
            response, "form", "password", "This password is too common."
        )


"""
---------------------------------------------------
Login tests
---------------------------------------------------
"""


@tag("auth", "views")
class LoginViewTestCase(UnitTest):
    def setUp(self):
        super().setUp()
        self.login_data = login_form_data(*create_random_user(self.rd))
        User.objects.create_user(
            username=self.login_data["username"],
            email=random_email(self.rd),
            password=self.login_data["password"],
        )

    def test_login(self):
        # Attempt to login as a valid user and test that login succeeded
        response = self.client.get(reverse("login"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, os.path.join("dashboard", "login.html"))

        self.client.post(reverse("login"), self.login_data)
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_invalid_login(self):
        # An invalid login should redirect to the login page
        username = random_username(self.rd)
        password = random_password(self.rd)
        login_data = {"username": username, "password": password}

        # Ensure we can't login
        self.client.login(username=username, password=password)
        self.assertFalse(get_user(self.client).is_authenticated)
        logout(self.client)

        # Attempt login through the login form
        self.client.post(reverse("login"), login_data)
        self.assertFalse(get_user(self.client).is_authenticated)

    def test_redirect_before_login(self):
        # A logged-out client should be redirected to the /login page
        logout(self.client)

        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))

        response = self.client.get("/")
        self.assertTrue(response.url.startswith(reverse("login")))

    def test_redirect_after_login(self):
        # If we try to visit a page before authenticating, we should
        # be redirected to that page after we've logged in.
        # By default, we should be redirected to the dashboard.
        response = self.client.post(reverse("login"), self.login_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))
        logout(self.client)

        # 2. If we're logged out and try to visit another page, then
        #    we should be redirected to that page after login through
        #    the login page.
        pages = ("user settings", "scoreboard", "active labs", "available labs")
        for page in pages:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 302)
            response = self.client.post(response.url, self.login_data)
            self.assertEqual(response.url, reverse(page))
            logout(self.client)

        # 3. There shouldn't be any redirection from the signup page
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

        # 4. In the special case where we try to visit the logout URL, we
        #    should be redirected to the dashboard after login.
        response = self.client.get(reverse("logout"))
        response = self.client.post(response.url, self.login_data)
        self.assertEqual(response.url, reverse("dashboard"))


"""
---------------------------------------------------
Logout tests
---------------------------------------------------
"""


@tag("auth", "views")
class LogoutViewTestCase(UnitTest):
    def setUp(self):
        super().setUp(create_user=True)
        self.form_data = signup_form_data(self.username, self.email, self.password)

    def test_logout(self):
        # Test the logout endpoint.
        # 1. Can login, then logout
        self.client.login(username=self.username, password=self.password)
        self.assertTrue(get_user(self.client).is_authenticated)
        self.client.get(reverse("logout"))
        self.assertFalse(get_user(self.client).is_authenticated)

        # 2. If already logged out, then the logout endpoint doesn't
        #    do anything. It should just redirect to login.
        response = self.client.get(reverse("logout"))
        self.assertFalse(get_user(self.client).is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))


"""
---------------------------------------------------
Settings tests
---------------------------------------------------
"""


@tag("user-settings", "views")
class SettingsViewTestCase(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)

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
        new_password = random_password(self.rd)
        form_data = {
            "old_password": self.password,
            "new_password": new_password,
            "new_repassword": new_password,
        }
        self.client.post(reverse("user settings"), form_data)
        user = User.objects.get(username=self.username)
        self.assertFalse(user.check_password(self.password))
        self.assertTrue(user.check_password(new_password))

    @tag("user")
    def test_change_password_with_incorrect_old_password(self):
        """Attempt to change password with an invalid old password."""
        new_password = random_password(self.rd)
        form_data = {
            "old_password": random_password(self.rd),
            "new_password": new_password,
            "new_repassword": new_password,
        }
        response = self.client.post(reverse("user settings"), form_data)
        user = User.objects.get(username=self.username)
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.check_password(new_password))
        self.assertFormError(
            response,
            "password_change_form",
            "old_password",
            "The password you entered was incorrect.",
        )

    @tag("user")
    def test_change_password_with_nonmatching_repassword(self):
        """Attempt to change password with nonmatching new passwords."""
        new_password = random_password(self.rd)
        form_data = {
            "old_password": self.password,
            "new_password": new_password,
            "new_repassword": random_password(self.rd),
        }
        response = self.client.post(reverse("user settings"), form_data)
        user = User.objects.get(username=self.username)
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.check_password(new_password))
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
        form_data = {
            "old_password": self.password,
            "new_password": new_password,
            "new_repassword": new_password,
        }
        response = self.client.post(reverse("user settings"), form_data)
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
        form_data = {
            "old_password": self.password,
            "new_password": "password",
            "new_repassword": "password",
        }
        response = self.client.post(reverse("user settings"), form_data)
        self.assertEqual(self.user.password, initial_pass)
        self.assertFormError(
            response,
            "password_change_form",
            "new_password",
            "This password is too common.",
        )
