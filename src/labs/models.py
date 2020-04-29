from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.db import models
from django.utils import timezone
from users.models import User
from uuid import uuid4

"""
---------------------------------------------------
LabEnvironment
---------------------------------------------------
"""


class LabEnvironment(models.Model):
    # A unique identifier for the lab
    id = models.UUIDField(primary_key=True, default=uuid4, unique=True)

    # The name of the lab. Set default=None to force an error if we try to
    # save a LabEnvironment to the database without a name.
    name = models.CharField(max_length=30, blank=False, default=None, unique=True)

    # Description of the lab
    description = models.CharField(max_length=1000)

    # Category that the lab falls into (e.g. reverse engineering, recon, etc.)
    category = models.CharField(max_length=50, blank=False)

    # URL of the Docker image for the lab. Set default=None to force an error
    # if we try to save a LabEnvironment to the database without a url.
    url = models.CharField(max_length=200, blank=False, default=None)

    # Protocol used by Guacamole to connect to the lab
    protocol = models.CharField(max_length=32, blank=False)

    # Port used to connect to the lab
    port = models.PositiveIntegerField(blank=False)

    # Date when the lab was uploaded
    date_uploaded = models.DateTimeField(default=timezone.now)
