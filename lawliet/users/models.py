import os

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.dispatch import receiver
from django.db.models.signals import post_save

"""
---------------------------------------------------
Profile
---------------------------------------------------
"""


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Profile image
    profile_image = models.ImageField(
        upload_to=os.path.join("profiles", "img"), blank=True, null=True
    )

    # Maximum number of environments a user can have running at any given time
    max_instances = models.PositiveSmallIntegerField(
        default=settings.DEFAULT_MAX_INSTANCES
    )

    # Number of instances that the user has up and running
    active_instances = models.PositiveSmallIntegerField(default=0)

    # Whether or not the user's email has been validated yet
    email_validated = models.BooleanField(default=False)


# Helper functions for the Profile model
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Associate a Profile with a User every time a new User is created
    if created:
        user = instance

        # Use meepy.png for default profile picture
        path = settings.DEFAULT_PROFILE_IMAGE
        filename = path.split(os.sep)[-1]
        with open(path, "rb") as f:
            img = ImageFile(f, name=filename)
            Profile.objects.create(user=instance, profile_image=img)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Whenever a User object is modified, we modify the user's corresponding
    # Profile object.
    instance.profile.save()
