import dotenv
import os
import random

from django.test import TestCase, Client, tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from .utils import *
from users.models import User

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

    def setUp(self, preauth=False):
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

        ### If preauth=True, then we create a new user corresponding to the given
        ### username, password, and email in the setup phase, and login
        ### automatically.
        if preauth:
            self.user = User.objects.create_user(
                email=self.email, username=self.username, password=self.password
            )
            self.client = Client()
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