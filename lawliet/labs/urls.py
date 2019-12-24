from django.conf.urls import url
from labs.views import *

urlpatterns = [
    url(r"^labs/generate-lab$", generate_lab, name="generate lab"),
    url(r"^labs/delete-lab$", delete_lab, name="delete lab"),
]
