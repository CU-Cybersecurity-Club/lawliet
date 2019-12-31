"""
Functional tests for the labs app.
"""

import os

from django.test import tag
from django.urls import reverse

from lawliet.test_utils import FunctionalTest
from users.models import User


@tag("labs")
class UploadNewLabTestCase(FunctionalTest):
    """
    Functional tests for uploading new labs to the site.
    """

    def setUp(self):
        super().setUp(preauth=True)
        self.lab_name = "My Test Lab"
        self.lab_description = "This is my test lab!"
        self.lab_url = "https://hub.docker.com/wshand/cutter"
        self.lab_header_image = os.path.abspath(
            os.path.join("assets", "img", "meepy.png")
        )
        self.lab_has_web_interface = True

    """
    Helper functions
    """

    def get_lab_button(self):
        sidebar = self.browser.find_element_by_id("sidebar-wrapper")
        sidebar_buttons = sidebar.find_elements_by_class_name("sidebar-button")
        buttons = list(filter(lambda btn: btn.text == "Labs", sidebar_buttons))
        self.assertEqual(len(buttons), 1)
        return buttons[0]

    def get_lab_submenu(self):
        return self.browser.find_element_by_id("lab-menu")

    def get_lab_submenu_button(self, label):
        menu = self.get_lab_submenu()
        buttons = menu.find_elements_by_class_name("list-group-item")
        buttons = list(filter(lambda btn: btn.text == label, buttons))
        self.assertEqual(len(buttons), 1)
        return buttons[0]

    """
    Tests
    """

    @tag("sidebar")
    def test_nonstaff_cannot_access_lab_upload_page(self):
        # Meepy wants to upload a new lab to the site. However, as a non-staff
        # user, she is unable to do so.
        # She clicks the "Labs" button on the sidebar. There isn't any button
        # to upload a new lab to the site.
        self.browser.get(self.live_server_url)
        self.get_lab_button().click()

        menu = self.get_lab_submenu()
        menu_buttons = menu.find_elements_by_class_name("list-group-item")
        for button in menu_buttons:
            self.assertFalse("Upload".lower() in button.text.lower())

        # As a staff user, Meepy sees this upload form.
        user = User.objects.get(username=self.username)
        user.is_staff = True
        user.save()

        self.browser.get(self.live_server_url)
        self.get_lab_button().click()
        self.get_lab_submenu_button("Upload new").click()

        self.wait_for(lambda: self.assertIn("Upload lab", self.browser.title))

    def test_upload_new_lab(self):
        user = User.objects.get(username=self.username)
        user.is_staff = True
        user.save()

        # Meepy goes to the "available labs" page. She sees that nobody has
        # added a new lab environment to the site yet.
        self.browser.get(f"{self.live_server_url}{reverse('available labs')}")
        lab_cards = self.browser.find_elements_by_class_name("available-lab-card")
        self.assertEqual(len(lab_cards), 0)

        # Meepy goes to the lab upload page, where she's presented with a form
        # for adding a new LabEnvironment to the site.
        self.browser.get(f"{self.live_server_url}{reverse('upload lab')}")

        self.wait_for(lambda: self.assertIn("Upload lab", self.browser.title))

        namebox = self.browser.find_element_by_id("id_name")
        descbox = self.browser.find_element_by_id("id_description")
        urlbox = self.browser.find_element_by_id("id_url")
        imgbox = self.browser.find_element_by_id("id_header_image")
        webbox = self.browser.find_element_by_id("id_has_web_interface")

        placeholders = {
            namebox: "Environment name",
            descbox: "Add a description of the lab environment",
            urlbox: "ex. https://hub.docker.com/r/wshand/cutter",
        }
        for box in placeholders:
            self.assertEqual(box.get_attribute("placeholder"), placeholders[box])

        # Meepy fills out all of the forms on the page to add a new lab environment
        namebox.send_keys(self.lab_name)
        descbox.send_keys(self.lab_description)
        urlbox.send_keys(self.lab_url)
        imgbox.send_keys(self.lab_header_image)

        # By default, the "has web interface" box should be selected.
        self.assertTrue(webbox.is_selected)

        # Meepy clicks the "save lab" button. She receives a message saying that her
        # lab was saved and uploaded to the server.
        save_button = self.browser.find_element_by_id("lab-save-button")
        self.assertEqual(save_button.text, "Save lab")
        save_button.click()

        alert = self.browser.find_element_by_class_name("alert-success")
        self.assertIn("Your environment was uploaded to the server", alert.text)

        # Meepy now goes to the "available labs" page and sees the environment she
        # added.
        self.browser.get(f"{self.live_server_url}{reverse('available labs')}")
        lab_cards = self.browser.find_elements_by_class_name("available-lab-card")
        self.assertEqual(len(lab_cards), 1)
        self.assertIn(self.lab_name, lab_cards[0].text)
        self.assertIn(self.lab_description, lab_cards[0].text)
