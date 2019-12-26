"""
Test site navigation (visiting different pages, using the sidebar and navbar, and
so on).
"""

from django.test import tag
from django.contrib.auth import get_user
from django.urls import reverse
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest
from users.models import User

import time


"""
---------------------------------------------------
Test landing page and redirects after login.
---------------------------------------------------
"""


@tag("navigation")
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

        # On the dashboard, she's presented with a large window showing her
        # username, current rank, and other information.
        jumbotron = self.browser.find_elements_by_class_name("jumbotron")
        self.assertEqual(len(jumbotron), 1)
        jumbotron = jumbotron[0]

        # - Username
        # - Rank
        self.assertTrue(self.username in jumbotron.text)
        self.assertTrue(self.user.profile.get_rank() in jumbotron.text)

        # - Profile image
        img = jumbotron.find_elements_by_tag_name("img")
        self.assertEqual(len(img), 1)
        img_src = img[0].get_attribute("src")
        self.assertTrue(img_src.endswith(self.user.profile.profile_image.name))

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

        # At the top of the sidebar, she sees a button with her username and profile
        # image. This button redirects her back to the dashboard.
        dashboard_url = self.browser.current_url
        profile_button = sidebar.find_elements_by_class_name("profile-card")
        self.assertEqual(len(profile_button), 1)

        profile_button = profile_button[0]
        profile_button_position = profile_button.location
        profile_button.click()
        self.assertEqual(self.browser.current_url, dashboard_url)

        # Below her profile information, she sees a list of buttons that redirect
        # her to various parts of the site.
        # - Labs
        # - Settings
        buttons = self.get_sidebar_buttons()
        self.assertEqual(len(buttons), 2)
        self.assertEqual(buttons[0].text, "Labs")
        self.assertEqual(buttons[1].text, "Settings")

        # First Meepy checks out the "Labs" sidebar button
        # (Tests omitted here -- see test_can_navigate_lab_submenu_in_sidebar)

        # Next, Meepy checks out the "Settings" button. Clicking this button
        # redirects her to the settings page.
        buttons[1].click()
        self.assertTrue(self.browser.current_url.endswith("settings"))
        self.assertTrue("Settings" in self.browser.title)

    @tag("sidebar")
    def test_can_navigate_lab_submenu_in_sidebar(self):
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
        # - Upload new
        menu_buttons = lab_menu.find_elements_by_class_name("list-group-item")
        self.assertEqual(len(menu_buttons), 3)

        data = zip(
            ["Available labs", "Active labs", "Upload new"],
            ["Labs", "Active lab", "Upload lab"],
            ["labs", "active-lab", "upload-lab"],
        )
        for (ii, (text, title, suffix)) in enumerate(data):
            # Meepy clicks one of the buttons on the submenu, and it redirects
            # her to a new page corresponding to the button's label.
            btn = lab_menu.find_elements_by_class_name("list-group-item")[ii]
            self.assertEqual(btn.text, text)
            btn.click()
            self.assertTrue(title in self.browser.title)
            self.assertTrue(self.browser.current_url.endswith(suffix))

            # Meepy clicks the "Lab" button on the sidebar again to expand
            # the lab submenu.
            self.get_sidebar_button("Labs").click()
            lab_menu = self.browser.find_element_by_id("lab-menu")


"""
---------------------------------------------------
Test the site's navbar
---------------------------------------------------
"""


@tag("navigation")
class NavbarNavigationTestCase(FunctionalTest):
    """
    Meepy wants to use the navbar at the top of the page.
    """

    def setUp(self):
        super().setUp(preauth=True)

    """
    Navbar tests
    """

    @tag("navbar", "sidebar", "auth")
    def test_use_navbar(self):
        # Meepy goes to the site. She sees a navbar at the top of the page
        self.browser.get(self.live_server_url)
        navbar = self.browser.find_elements_by_tag_name("nav")
        self.assertEqual(len(navbar), 1)
        navbar = navbar[0]
        self.assertEqual(navbar.location["y"], 0)

        # The navbar sits right next to the sidebar on the left, and hugs
        # the edge of the window on the right.
        sidebar = self.browser.find_element_by_id("sidebar-wrapper")
        window_size = self.browser.get_window_size()
        self.assertEqual(navbar.location["x"], sidebar.size["width"])
        self.assertEqual(
            navbar.size["width"] + sidebar.size["width"], window_size["width"]
        )

        # Meepy clicks the "hamburger" icon on the navbar. This causes the
        # sidebar to compress. She clicks it again and the sidebar reappears.
        wrapper = self.browser.find_element_by_id("wrapper")
        self.assertFalse("toggled" in wrapper.get_attribute("class"))

        hamburger = navbar.find_element_by_id("sidebar-toggle")
        hamburger.click()
        time.sleep(0.25)
        self.assertTrue("toggled" in wrapper.get_attribute("class"))
        self.assertEqual(navbar.size["width"], window_size["width"])

        hamburger.click()
        time.sleep(0.25)
        self.assertFalse("toggled" in wrapper.get_attribute("class"))
        self.assertEqual(
            navbar.size["width"] + sidebar.size["width"], window_size["width"]
        )

        # Meepy clicks the "logout" button on the navbar, de-authenticating
        # in the process.
        logout_button = navbar.find_element_by_id("logout-button")
        logout_button.click()
        self.assertFalse(get_user(self.client).is_authenticated)
