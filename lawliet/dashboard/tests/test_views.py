"""
Tests for the views offered by the dashboard app.
"""
import os
import random

from django.test import TestCase, Client
from django.contrib.auth import get_user, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from uuid import UUID

from .utils import *

"""
---------------------------------------------------
Signup tests
---------------------------------------------------
"""


class SignupViewTestCase(TestCase):
    def setUp(self):
        # Set up RNG to get reproducible results
        self.rd = random.Random()
        self.rd.seed(0)

        self.client = Client()
        self.username, self.email, self.password = create_random_user(self.rd)
        self.form_data = signup_form_data(self.username, self.email, self.password)

    def test_signup(self):
        # Create a new user and check that they were
        # registered in the database.
        response = self.client.post("/signup", self.form_data)

        user = User.objects.get(username=self.username)
        self.assertEqual(len(User.objects.all()), 1)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

    def test_invalid_signups(self):
        # An invalid signup shouldn't modify the database
        # 1. Add a valid user
        self.client.post("/signup", self.form_data)
        self.assertEqual(len(User.objects.all()), 1)
        users = list(User.objects.all())

        # 2-4: attempt to sign up with the following invalidating
        #      conditions:
        #      - Username already taken
        #      - Provided email already registered
        #      - Passwords don't match
        kv_pairs = [
            ("username", self.username),
            ("email", self.email),
            ("password", random_password(self.rd)),
        ]
        for (key, val) in kv_pairs:
            form_data = random_signup_form(self.rd)
            form_data[key] = val
            response = self.client.post("/signup", form_data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(users, list(User.objects.all()))


"""
---------------------------------------------------
Login tests
---------------------------------------------------
"""


class LoginViewTestCase(TestCase):
    def setUp(self):
        # Set up RNG to get reproducible results
        self.rd = random.Random()
        self.rd.seed(0)

        self.client = Client()
        self.login_data = login_form_data(*create_random_user(self.rd))

        User.objects.create_user(
            username=self.login_data["username"],
            email=random_email(self.rd),
            password=self.login_data["password"],
        )

    def test_login(self):
        # Attempt to login as a valid user and test that login succeeded
        self.client.post(reverse("login"), self.login_data)
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_invalid_login(self):
        # An invalid login should redirect to the login page
        username = random_username(self.rd)
        password = random_password(self.rd)
        login_data = {"username": username, "password": password}

        # Ensure we can't login programmatically
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


class LogoutViewTestCase(TestCase):
    def setUp(self):
        # Set up RNG to get reproducible results
        self.rd = random.Random()
        self.rd.seed(0)

        self.client = Client()
        self.username, self.email, self.password = create_random_user(self.rd)
        self.form_data = signup_form_data(self.username, self.email, self.password)

        User.objects.create_user(
            username=self.username, email=random_email(self.rd), password=self.password
        )

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
