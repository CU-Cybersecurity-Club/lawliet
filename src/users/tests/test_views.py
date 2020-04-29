"""
Tests for authentication-related views.
"""

import os
import re

from django.core import mail
from django.conf import settings
from django.contrib.auth import get_user, login, logout
from django.test import tag
from django.urls import reverse
from lawliet.test_utils import UnitTest, random_email, random_username, random_password
from unittest import skip
from users.models import User, EmailVerificationToken

"""
---------------------------------------------------
Global variables
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
        self.form_data = {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "repassword": self.password,
        }

    @tag("email")
    def test_signup(self):
        """
        Create a new user and check that they were registered in the database.
        """
        response = self.client.get(reverse("signup"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "signup.html")

        response = self.client.post(reverse("signup"), self.form_data)

        self.assertEqual(len(User.objects.all()), 1)

        user = User.objects.get(username=self.username)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

        # TODO: re-enable email verification
        # User should be disabled until they verify their email address. A new
        # token should have been created and sent to the user for them to verify
        # their address.
        # self.assertFalse(user.is_active)
        # self.assertEqual(len(mail.outbox), 1)

        # self.assertEqual(len(EmailVerificationToken.objects.all()), 1)
        # token = EmailVerificationToken.objects.get(email=self.email)

        # The token carries a URL that, when visited, activates the user's account.
        # response = self.client.get(token.email_verification_location)
        # self.assertTrue(User.objects.get(username=self.username).is_active)

    def test_signup_as_registered_email_or_user(self):
        """
        Attempt to sign up as new user with registered email address or username.
        """
        # Start by adding a new user to the database
        user = User.objects.create_user(
            email=self.email, username=self.username, password=self.password
        )

        # Attempt to sign up a user with the same email
        newpass = random_password(self.rd)
        form_data = {
            "email": self.email,
            "username": random_username(self.rd),
            "password": newpass,
            "repassword": newpass,
        }
        response = self.client.post(reverse("signup"), form_data)

        self.assertEqual(len(User.objects.all()), 1)
        self.assertEqual(user, User.objects.get(email=self.email))
        self.assertFormError(
            response, "form", "email", "User with this Email already exists."
        )

        # Attempt to sign up a user with the same username
        form_data["email"] = random_email(self.rd)
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
        super().setUp(create_user=True)
        self.login_data = {"username": self.username, "password": self.password}

    def test_login(self):
        # Attempt to login as a valid user and test that login succeeded
        response = self.client.get(reverse("login"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "login.html")

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
        pages = ("user settings", "active labs", "available labs")
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

    def test_deactivated_users_cannot_login(self):
        """It should be impossible to login with a deactivated account."""
        # Deactivate the account we created in setUp
        user = User.objects.get(username=self.username)
        user.is_active = False
        user.save()

        # Attempt to log in with the user's credentials
        response = self.client.post(reverse("login"), self.login_data)
        self.assertFalse(get_user(self.client).is_authenticated)
        msg = "This user's account is currently deactivated."
        self.assertFormError(response, "form", None, msg)

    def test_error_if_login_attempted_with_unverified_email(self):
        """
        If the user account is currently deactivated and there's an
        EmailVerificationToken out on them, then the login form should reflect
        that when we attempt to log in.
        """
        user = User.objects.get(username=self.username)
        user.is_active = False
        user.save()

        token = EmailVerificationToken.objects.create(
            username=self.username, email=self.email
        )
        response = self.client.post(reverse("login"), self.login_data)
        msg = "You must verify your email address before you can login."
        self.assertFormError(response, "form", None, msg)


"""
---------------------------------------------------
Email verification tests
---------------------------------------------------
"""


@tag("auth", "email", "views")
class EmailVerificationTestCase(UnitTest):
    def setUp(self):
        super().setUp()

        # POST data to the signup form as if to sign up as a new user
        signup_data = {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "repassword": self.password,
        }
        self.client.post(reverse("signup"), data=signup_data)

    @skip("TODO")
    def test_verify_email(self):
        # After attempting to sign up as a new user, check the outbox to
        # get the link to verify email.
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertIn(self.email, email.to)
        self.assertEqual(email.subject, "Finish signing up for Lawliet")

        # Within the email sent to the user, there should be a link that they can
        # click to verify their address.
        self.assertIn("Use this link to log in", email.body)
        url_search = re.search(r"http://.+/.+$", email.body)
        if not url_search:
            self.fail(f"Could not find URL in email body:\b{email_body}")
        url = url_search.group(0)

        token = EmailVerificationToken.objects.get(email=self.email)
        self.assertTrue(url.endswith(f"uid={token.uid}"))

        # If the user visits that link, their email should become verified and
        # their account should be activated.
        self.client.get(url)
        self.assertTrue(User.objects.get(username=self.username).is_active)


"""
---------------------------------------------------
Logout tests
---------------------------------------------------
"""


@tag("auth", "views")
class LogoutViewTestCase(UnitTest):
    def setUp(self):
        super().setUp(create_user=True)

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
User API tests
---------------------------------------------------
"""


@tag("user-api")
class UserAPITestCase(UnitTest):
    def setUp(self):
        super().setUp(preauth=True)

    def test_get_user_info(self):
        pass
