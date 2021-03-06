"""
Test site navigation (visiting different pages, using the sidebar and navbar, and
so on).
"""

from django.test import tag
from django.contrib.auth import get_user
from django.urls import reverse
from selenium.webdriver.common.keys import Keys
from unittest import skip

from lawliet.test_utils import FunctionalTest
from users.models import User

"""
---------------------------------------------------
Test landing page and redirects after login.
---------------------------------------------------
"""


@tag("navigation")
@skip("TODO")
class UserDashboardTestCase(FunctionalTest):
    """
    Meepy has signed up to the site, and is now navigating her dashboard and
    checking out the basic interface offered by the site.
    """

    def setUp(self):
        super().setUp(preauth=False)

        # Create a user corresponding to the generated credentials
        self.user = User.objects.create_user(
            email=self.email, username=self.username, password=self.password
        )

    """
    Dashboard tests
    """

    @tag("auth")
    def test_user_dashboard(self):
        # Meepy visits the site and is directed to the login page, where she
        # logs in with her credentials.
        self.browser.get(self.live_server_url)
        self.assertIn("Login", self.browser.title)

        userbox = self.browser.find_element_by_id("id_username")
        passbox = self.browser.find_element_by_id("id_password")
        userbox.send_keys(self.username)
        passbox.send_keys(self.password)
        self.browser.find_element_by_id("login-button").click()

        # After entering her credentials, she is redirected to her dashboard
        self.assertIn("Dashboard", self.browser.title)
        self.assertTrue(self.browser.current_url.endswith("dashboard"))

    @tag("auth")
    def test_redirect_after_login(self):
        # Meepy tries to visit a few different pages, but isn't logged in yet.
        urls = [reverse("user settings"), reverse("dashboard")]
        for url in urls:
            self.browser.get(self.live_server_url + url)
            self.assertIn("Login", self.browser.title)
            self.assertTrue(self.browser.current_url.endswith(f"/login?next={url}"))

            userbox = self.browser.find_element_by_id("id_username")
            passbox = self.browser.find_element_by_id("id_password")
            userbox.send_keys(self.username)
            passbox.send_keys(self.password)
            self.browser.find_element_by_id("login-button").click()

            # After logging in to the site, she is redirected to the page that
            # she was trying to visit.
            self.assertTrue(self.browser.current_url.endswith(url))

            # We wipe the cookies from Meepy's browser to emulate logging out
            self.browser.delete_all_cookies()


"""
---------------------------------------------------
Test the site's sidebar
---------------------------------------------------
"""


@tag("navigation")
@skip("TODO")
class SidebarNavigationTestCase(FunctionalTest):
    """
    Meepy would like to try to navigate through the site using the sidebar
    """

    def setUp(self):
        super().setUp(preauth=True)

    """
    Helper functions
    """

    def get_sidebar(self):
        return self.browser.find_element_by_id("sidebar-wrapper")

    def get_sidebar_buttons(self):
        return self.get_sidebar().find_elements_by_class_name("sidebar-button")

    def get_sidebar_button(self, label):
        buttons = self.get_sidebar_buttons()
        buttons = list(filter(lambda btn: btn.text == label, buttons))
        self.assertEqual(len(buttons), 1)
        return buttons[0]

    """
    Sidebar tests
    """

    @tag("sidebar")
    def test_navigate_site_through_sidebar(self):
        # Meepy visits the site, and notices the sidebar on the left side of the page
        self.browser.get(self.live_server_url)
        sidebar = self.get_sidebar()
        self.assertEqual(sidebar.location, {"x": 0, "y": 0})

        # Below her profile information, she sees a list of buttons that redirect
        # her to various parts of the site.
        # - Dashboard
        # - Labs
        # - Settings
        labels = ["Dashboard", "Labs", "Settings"]
        buttons = self.get_sidebar_buttons()
        self.assertEqual(len(buttons), len(labels))
        for (btn, label) in zip(buttons, labels):
            self.assertEqual(btn.text, label)

        # Meepy clicks the "Dashboard" button. It redirects her back to the
        # dashboard.
        buttons[0].click()
        self.assertTrue(self.browser.current_url.endswith("dashboard"))
        self.assertTrue("Dashboard" in self.browser.title)
        buttons = self.get_sidebar_buttons()

        # Meepy checks out the "Labs" sidebar button
        # (Tests omitted here -- see test_can_navigate_lab_submenu_in_sidebar)

        # Meepy checks out the "Settings" button. Clicking this button
        # redirects her to the settings page.
        buttons[2].click()
        self.assertTrue(self.browser.current_url.endswith("settings"))
        self.assertTrue("Settings" in self.browser.title)

    @tag("sidebar")
    def test_can_navigate_lab_submenu_in_sidebar(self):
        for is_staff in (False, True):
            self.user.is_staff = is_staff
            self.user.save()

            # Meepy goes back to the site and checks out the sidebar. On the sidebar,
            # she sees a button with the label "Labs". She clicks the button, causing
            # a collapsible menu to expand.
            self.browser.get(self.live_server_url)
            lab_button = self.get_sidebar_button("Labs")
            lab_menu = self.browser.find_element_by_id("lab-menu")
            self.assertEqual(lab_menu.value_of_css_property("display"), "none")
            lab_button.click()
            self.assertNotEqual(lab_menu.value_of_css_property("display"), "none")

            # Within the labs submenu, Meepy sees the following options:
            # - Available labs
            # - Active labs
            #
            # As a staff member, Meepy would also see a third option:
            # - Upload new
            data = (
                # Button label / page title / button id
                ("Available labs", "Labs", "labs"),
                ("Active labs", "Active lab", "active-lab"),
                ("Upload new", "Upload lab", "upload-lab"),
            )

            num_buttons = 2 if not is_staff else 3

            menu_buttons = lab_menu.find_elements_by_class_name("list-group-item")
            self.assertEqual(len(menu_buttons), num_buttons)

            for (ii, (text, title, suffix)) in enumerate(data[:num_buttons]):
                # Meepy clicks one of the buttons on the submenu, and it redirects
                # her to a new page corresponding to the button's label.
                btn = lab_menu.find_elements_by_class_name("list-group-item")[ii]
                self.assertEqual(btn.text, text)
                btn.click()
                self.assertTrue(title in self.browser.title)
                self.assertTrue(self.browser.current_url.endswith(suffix))

                # Meepy doesn't need to click the "Lab" button again, because the
                # sidebar is still expanded after clicking a button in the lab
                # submenu.
                lab_menu = self.browser.find_element_by_id("lab-menu")
