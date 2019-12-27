import os

from django.db import models
from django.conf import settings
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.images import ImageFile
from django.core.validators import RegexValidator, MinLengthValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

from .managers import UserManager

"""
Settings for the User and Profile models
"""
"""User options"""
MAX_EMAIL_ADDRESS_LENGTH = 150
MAX_USERNAME_LENGTH = 20
MIN_USERNAME_LENGTH = 3

"""Profile options"""
DEFAULT_PROFILE_IMAGE = os.path.join(settings.BASE_DIR, "assets", "img", "meepy.png")

# Default maximum number of lab environments that a user can run
# at a given time.
DEFAULT_MAX_INSTANCES = 1

"""
---------------------------------------------------
Custom User model
---------------------------------------------------
"""


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                r"^[\w\.\-_]+$",
                (
                    "Your username may only contain letters, numbers, periods "
                    "(.), dashes (-), and underscores (_)."
                ),
            ),
            MinLengthValidator(MIN_USERNAME_LENGTH),
        ],
    )

    email = models.EmailField(max_length=MAX_EMAIL_ADDRESS_LENGTH, unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self):
        return self.username


class UserAdmin(ModelAdmin):
    pass


"""
---------------------------------------------------
Profile
---------------------------------------------------
"""

# Mapping of integer ranks to rank names
USER_RANKS = {0: "Beginner"}

# Name to use for integer ranks whose corresponding names haven't been defined
UNKNOWN_RANK = "Unknowable Void"


def integer_rank_to_string(rank):
    """Function to convert a Profile's integer rank to the corresponding rank's name"""
    return USER_RANKS.get(rank, UNKNOWN_RANK)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Profile image
    profile_image = models.ImageField(
        upload_to=os.path.join("profiles", "img"), blank=True, null=True
    )

    # User's current score and rank
    score = models.PositiveIntegerField(default=0, blank=False)
    rank = models.PositiveSmallIntegerField(default=0, blank=False)

    # User-supplied description of themselves
    description = models.CharField(max_length=1000, default="", blank=True)

    # Maximum number of environments a user can have running at any given time
    max_instances = models.PositiveSmallIntegerField(default=DEFAULT_MAX_INSTANCES)

    # Number of instances that the user has up and running
    active_instances = models.PositiveSmallIntegerField(default=0)

    # Whether or not the user's email has been validated yet
    email_verified = models.BooleanField(default=False)

    """
    Helper functions
    """

    @property
    def get_rank(self):
        return integer_rank_to_string(self.rank)


# Helper functions for the Profile model
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Associate a Profile with a User every time a new User is created
    if created:
        user = instance

        # Use meepy.png for default profile picture
        path = DEFAULT_PROFILE_IMAGE
        filename = path.split(os.sep)[-1]
        with open(path, "rb") as f:
            img = ImageFile(f, name=filename)
            Profile.objects.create(user=instance, profile_image=img)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Whenever a User object is modified, we modify the user's corresponding
    # Profile object.
    instance.profile.save()
