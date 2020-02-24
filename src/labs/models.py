import os

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
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
    name = models.CharField(max_length=30, blank=False, default=None)

    # Description of the lab
    description = models.CharField(max_length=1000)

    # URL of the Docker image for the lab. Set default=None to force an error
    # if we try to save a LabEnvironment to the database without a url.
    url = models.URLField(max_length=100, blank=False, default=None)

    # Boolean field that specifies whether or not the lab has a web interface
    has_web_interface = models.BooleanField(default=True)
