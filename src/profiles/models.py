from django.core.files.images import ImageFile
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

"""Profile options"""
DEFAULT_PROFILE_IMAGE = os.path.join(settings.BASE_DIR, "assets", "img", "meepy.png")

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
