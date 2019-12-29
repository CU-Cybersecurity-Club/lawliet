"""
Various helpful functions and classes for running tests.
"""

import dotenv
import os
import random

from django.test import TestCase, Client, tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from uuid import UUID

from users.models import User


"""
---------------------------------------------------
Helper functions
---------------------------------------------------
"""

# Methods for randomly generating fields for User instances
random_uuid = lambda rd: UUID(int=rd.getrandbits(128)).hex
random_username = lambda rd: f"meepy-{random_uuid(rd)[:10]}"
random_email = lambda rd: f"meepy-{random_uuid(rd)[:10]}@colorado.edu"
random_password = lambda rd: random_uuid(rd)
random_docker_image = (
    lambda rd: "https://hub.docker.com/r/meepy/{random_uuid(rd)[:10]}:{random_uuid(rd)[:10]}"
)

# Generate all of the data for a new user, consisting of a username,
# an email, and a password.
def create_random_user(rd):
    username = random_username(rd)
    email = random_email(rd)
    password = random_password(rd)
    return username, email, password


# Create the data required by a POST request to /signup for signing up a
# new user
def signup_form_data(username, email, password):
    return {
        "username": username,
        "email": email,
        "password": password,
        "repassword": password,
    }


# Create the data required by a POST request to /login to log into a
# service.
def login_form_data(username, email, password):
    return {"username": username, "password": password}


# Create a random user and put their data into a dictionary to be given
# in a POST request to /signup.
def random_signup_form(rd):
    return signup_form_data(*create_random_user(rd))


# Create a random user and put their data into a dictionary to be given
# in a POST request to /login.
def random_login_form(rd):
    return login_form_data(*create_random_user(rd))


"""
---------------------------------------------------
Functional testing base class
---------------------------------------------------
"""


@tag("functional-tests")
class FunctionalTest(StaticLiveServerTestCase):
    """
    Base class for functional tests.
    """

    def setUp(self, create_user=False, preauth=False):
        ### Seed RNG for consistent results
        self.rd = random.Random()
        self.rd.seed(0)

        ### Create a Selenium WebDriver to run functional tests
        self.browser = webdriver.Firefox()

        dotenv.load_dotenv()
        staging_server = os.getenv("STAGING_SERVER")
        if staging_server:
            self.live_server_url = staging_server

            # Authenticate to staging server
            self.fail("TODO")

        # Create a test username, email, and password
        self.username = random_username(self.rd)
        self.password = random_password(self.rd)
        self.email = random_email(self.rd)

        ### If preauth or create_user == True, then create a new user for the
        ### test. In addition, if preauth == True, then we automatically log
        ### in as the user.
        self.client = Client()
        if preauth or create_user:
            self.user = User.objects.create_user(
                email=self.email, username=self.username, password=self.password
            )

        if preauth:
            self.client.force_login(self.user)
            cookie = self.client.cookies["sessionid"]
            self.browser.get(self.live_server_url)
            self.browser.add_cookie(
                {
                    "name": "sessionid",
                    "value": cookie.value,
                    "secure": False,
                    "path": "/",
                }
            )

    def tearDown(self):
        self.browser.quit()


"""
---------------------------------------------------
Unit testing base class
---------------------------------------------------
"""


@tag("unit-tests")
class UnitTest(TestCase):
    def setUp(self, seed=0, create_user=False, preauth=False):
        self.client = Client()

        ### Seed RNG to ensure consistent results.
        self.rd = random.Random()
        self.rd.seed(seed)

        ### Generate a random username, email address, and password that
        ### child classes can use to create their own user.
        self.email = random_email(self.rd)
        self.username = random_username(self.rd)
        self.password = random_password(self.rd)

        ### If create_user or preauth is True, create a new user with the
        # generated information in advance. If preauth=True then we also
        # login the client as the new user.
        if preauth or create_user:
            self.user = User.objects.create_user(
                email=self.email, username=self.username, password=self.password
            )
        if preauth:
            self.client.force_login(self.user)
