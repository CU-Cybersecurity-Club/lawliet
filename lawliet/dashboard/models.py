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
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=1000)
    url = models.URLField(max_length=100)
    header_image = models.ImageField(upload_to=os.path.join("labs", "img"))
