from django.conf.urls import url
from labs.views import *

urlpatterns = [
    url(r"^generate-lab$", generate_lab, name="generate lab"),
    url(r"^delete-lab$", delete_lab, name="delete lab"),
    url(r"^lab-status$", lab_status, name="lab status"),
]
