from django.test import tag
from selenium.webdriver.common.keys import Keys

from .ft_base import FunctionalTest
from .utils import *
from users.models import User

"""
---------------------------------------------------
Test authentication (login and signup) for the site.
---------------------------------------------------
"""


@tag("auth")
class NewVisitorTestCase(FunctionalTest):
    """
    Meepy the Anthropomorphic Router visits the site, and decides that she
    would like to sign up as a new user.
    """

    def test_cannot_login_as_nonexistent_user(self):
        # Meepy visits the Lawliet site and is immediately directed to its login
        # page.
        self.browser.get(self.live_server_url)
        self.assertIn("Login", self.browser.title)
        self.assertTrue(self.browser.current_url.endswith("/login"))
        login_url = self.browser.current_url

        # Meepy tries to login but realizes that she hasn't signed up yet. Oops!
        userbox = self.browser.find_element_by_id("id_username")
        passbox = self.browser.find_element_by_id("id_password")

        self.assertEqual(userbox.get_attribute("placeholder"), "Username")
        self.assertEqual(passbox.get_attribute("placeholder"), "Password")

        userbox.send_keys(self.username)
        passbox.send_keys(self.password)

        self.browser.find_element_by_id("login-button").click()

        # She gets redirected back to the login page, and an error shows up.
        msg = f"The user with username '{self.username}' could not be found."
        self.assertIn(msg, self.browser.page_source)
        self.assertEqual(login_url, self.browser.current_url)

    def test_can_sign_up_as_new_user(self):
        # Meepy decides to register as a new user. She visits the site again, and
        # clicks the 'signup' button.
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id("signup-redirect-button").click()
        self.assertIn("Sign up", self.browser.title)
        self.assertTrue(self.browser.current_url.endswith("/signup"))

        # She enters some credentials and hits the "sign up" button
        emailbox = self.browser.find_element_by_id("id_email")
        userbox = self.browser.find_element_by_id("id_username")
        passbox = self.browser.find_element_by_id("id_password")
        repassbox = self.browser.find_element_by_id("id_repassword")

        self.assertEqual(
            emailbox.get_attribute("placeholder"), "Enter your email address"
        )
        self.assertEqual(userbox.get_attribute("placeholder"), "Select a username")
        self.assertEqual(passbox.get_attribute("placeholder"), "Choose a password")
        self.assertEqual(
            repassbox.get_attribute("placeholder"), "Enter your password again"
        )

        emailbox.send_keys(self.email)
        userbox.send_keys(self.username)
        passbox.send_keys(self.password)
        repassbox.send_keys(self.password)

        self.browser.find_element_by_id("signup-button").click()

        # TODO: email verification

        # Meepy gets redirected to the login page, where she can now login with the
        # credentials she used to sign up
        userbox = self.browser.find_element_by_id("id_username")
        passbox = self.browser.find_element_by_id("id_password")

        userbox.send_keys(self.username)
        passbox.send_keys(self.password)

        self.browser.find_element_by_id("login-button").click()

        # After logging in, Meepy is redirected to her dashboard
        self.assertIn("Dashboard", self.browser.title)
        self.assertTrue(self.browser.current_url.endswith("/dashboard"))

        self.fail("TODO (email authentication)")


"""
---------------------------------------------------
Functional tests for various edge cases and errors involving the
signup form.
---------------------------------------------------
"""


@tag("auth")
class InvalidSignupTestCase(FunctionalTest):

    """
    Helper functions
    """

    def sign_up(self, email, username, password, repassword=None):
        repassword = repassword if repassword else password

        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id("signup-redirect-button").click()
        self.browser.find_element_by_id("id_email").send_keys(email)
        self.browser.find_element_by_id("id_username").send_keys(username)
        self.browser.find_element_by_id("id_password").send_keys(password)
        self.browser.find_element_by_id("id_repassword").send_keys(repassword)
        self.browser.find_element_by_id("signup-button").click()

    """
    Tests
    """

    def test_nonmatching_passwords(self):
        # Meepy tries to sign up for the site, but enters different passwords
        # in the password fields. Her signup is unsuccessful, and the site
        # displays an error message to her.
        self.assertEqual(len(User.objects.all()), 0)
        self.sign_up(
            self.email,
            self.username,
            random_password(self.rd),
            repassword=random_password(self.rd),
        )
        self.assertEqual(len(User.objects.all()), 0)

        alerts = self.browser.find_elements_by_class_name("form-error")
        self.assertEqual(len(alerts), 1)
        self.assertEqual(
            alerts[0].text,
            "The passwords you've entered don't match. Please try again.",
        )

    def test_signup_with_existing_username_or_email(self):
        # Somebody else comes along and creates a user with the username and
        # email address that Meepy wants to sign up with.
        user = User.objects.create_user(
            email=self.email, username=self.username, password=random_password(self.rd)
        )
        user_password = user.password

        # Meepy tries to sign up for the site. First, she tries to sign up with
        # an email address that already has an account.
        self.assertEqual(len(User.objects.all()), 1)
        self.sign_up(self.email, random_username(self.rd), self.password)
        self.assertEqual(len(User.objects.all()), 1)

        alerts = self.browser.find_elements_by_class_name("form-error")
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].text, "User with this Email already exists.")

        # (Existing user's password should not have been modified)
        self.assertEqual(User.objects.get(email=self.email).password, user_password)

        # Failing that, Meepy tries to sign up with a username that's already
        # been registered.
        self.sign_up(random_email(self.rd), self.username, self.password)
        self.assertEqual(len(User.objects.all()), 1)

        alerts = self.browser.find_elements_by_class_name("form-error")
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].text, "User with this Username already exists.")

        # (Existing user's password should not have been modified)
        self.assertEqual(
            User.objects.get(username=self.username).password, user_password
        )

    def test_signup_with_invalid_password(self):
        # Meepy tries to sign up with a password that's too short.
        self.assertEqual(len(User.objects.all()), 0)
        self.sign_up(self.email, self.username, random_password(self.rd)[:6])
        self.assertEqual(len(User.objects.all()), 0)

        # Note: signup button should be disabled, there should be a min length
        # attribute on the password and repassword inputs.

        # Meepy tries to sign up with a password that's too basic
        self.sign_up(self.email, self.username, "password")
        self.assertEqual(len(User.objects.all()), 0)

        alerts = self.browser.find_elements_by_class_name("form-error")
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].text, "This password is too common.")

    def test_return_to_login_with_filled_fields(self):
        # Meepy fills in all the fields of the signup form, but decides to
        # return to the login form.
        self.assertEqual(len(User.objects.all()), 0)
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id("signup-redirect-button").click()
        self.browser.find_element_by_id("id_email").send_keys(self.email)
        self.browser.find_element_by_id("id_username").send_keys(self.username)
        self.browser.find_element_by_id("id_password").send_keys(self.password)
        self.browser.find_element_by_id("id_repassword").send_keys(self.password)
        self.browser.find_element_by_id("login-redirect-button").click()
        self.assertEqual(len(User.objects.all()), 0)
