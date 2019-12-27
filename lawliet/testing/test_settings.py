"""
Test various user settings.
"""

from django.test import tag

from .base import FunctionalTest
from users.models import User

"""
---------------------------------------------------
Test changing user settings through the ProfileForm
---------------------------------------------------
"""


@tag("users", "user-settings")
class UserProfileTestCase(FunctionalTest):
    """
    Meepy signs into her account. She wants to change some of the default
    settings for her user.
    """

    def setUp(self):
        super().setUp(preauth=True)

    """
    Helper functions
    """

    def go_to_settings_page(self):
        self.browser.get(self.live_server_url)
        sidebar = self.browser.find_element_by_id("sidebar-wrapper")
        buttons = sidebar.find_elements_by_class_name("sidebar-button")
        buttons = list(filter(lambda btn: btn.text == "Settings", buttons))
        self.assertEqual(len(buttons), 1)
        buttons[0].click()

    """
    Tests
    """

    def test_view_profile_information(self):
        # Meepy goes to her settings page. Her profile settings are initially
        # hidden, but after clicking the "Profile options" button, she is shown a
        # variety of different profile options she can change.
        self.go_to_settings_page()
        profile_button = self.browser.find_element_by_id("list-profile-list")
        profile_panel = self.browser.find_element_by_id("list-profile")
        self.assertEqual(profile_button.text, "Profile options")
        self.assertEqual(profile_panel.value_of_css_property("display"), "none")

        profile_button.click()
        self.assertNotEqual(profile_panel.value_of_css_property("display"), "none")

        # On the profile settings page, she sees two columns. In the left column,
        # there's a list of labels for different profile options. In the right
        # column, there are widgets she can use to modify her profile.
        lcol = profile_panel.find_elements_by_class_name("col-4")
        rcol = profile_panel.find_elements_by_class_name("col-6")
        self.assertEqual(len(lcol), len(rcol))

        # The first row is for her profile image.
        self.assertEqual(lcol[0].text, "Profile image")
        img_src = rcol[0].find_element_by_tag_name("img").get_attribute("src")
        self.assertTrue(img_src.endswith(self.user.profile.profile_image.name))

        # The second row is for the user's description
        self.assertEqual(lcol[1].text, "Description")
        textarea = rcol[1].find_element_by_tag_name("textarea")
        self.assertEqual(
            textarea.get_attribute("placeholder"), "Describe yourself here"
        )

    def test_change_user_description(self):
        # Meepy goes to her settings page, and hits the "Profile options" tab.
        self.go_to_settings_page()
        profile_button = self.browser.find_element_by_id("list-profile-list")
        profile_panel = self.browser.find_element_by_id("list-profile")
        profile_button.click()

        # Meepy goes to the row corresponding to her description.
        lcol = profile_panel.find_elements_by_class_name("col-4")
        rcol = profile_panel.find_elements_by_class_name("col-6")
        filterfn = lambda ii: (lcol[ii].text == "Description")
        rownum = list(filter(filterfn, range(len(lcol))))
        self.assertEqual(len(rownum), 1)
        rownum = rownum[0]

        # Meepy enters in a new profile description, and clicks the "save" button
        textarea = rcol[rownum].find_element_by_tag_name("textarea")
        textarea.send_keys("Hi! I'm Meepy!")
        profile_panel.find_element_by_id("profile-change-submit-button").click()

        # The page refreshes, showing her her updated profile description. The
        # new description has also been saved to the database.
        self.assertEqual(self.user.profile.description, "Hi! I'm Meepy!")
        textarea = (
            self.browser.find_element_by_id("list-profile")
            .find_elements_by_class_name("col-6")[rownum]
            .find_element_by_class_name("textarea")
        )
        self.assertEqual(textarea.text, "Hi! I'm Meepy!")
