from django.test import TestCase
from unittest import skip

"""
---------------------------------------------------
Profile tests
---------------------------------------------------
"""


@skip("Skipping Profile tests")
@tag("auth", "profiles")
class ProfileTestCase(UnitTest):
    def setUp(self):
        super().setUp(create_user=True)

        # New users should use the default profile image
        path = DEFAULT_PROFILE_IMAGE
        filename = path.split(os.sep)[-1]
        with open(path, "rb") as img:
            self.profile_image = SimpleUploadedFile(
                name=filename, content=img.read(), content_type="image/png"
            )

    def test_can_create_profile(self):
        user = User.objects.get(username=self.username)
        profile_image = user.profile.profile_image
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.profile.max_instances, DEFAULT_MAX_INSTANCES)
        self.assertEqual(user.profile.active_instances, 0)
        self.assertTrue(profile_image.name.startswith(os.path.join("profiles", "img")))

        with open(DEFAULT_PROFILE_IMAGE, "rb") as f:
            img = f.read()
            self.assertEqual(img, profile_image.read())
