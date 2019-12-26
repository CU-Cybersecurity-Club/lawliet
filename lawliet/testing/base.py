import dotenv
import os
import random

from django.test import Client, tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from .utils import *
from users.models import User


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
