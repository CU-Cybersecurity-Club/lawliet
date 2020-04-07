from django.conf.urls import url
from labs.views import *

urlpatterns = [
    url(r"^generate-lab$", GenerateLabView.as_view(), name="generate lab"),
    url(r"^delete-lab$", DeleteLabView.as_view(), name="delete lab"),
    url(r"^lab-status$", LabStatusView.as_view(), name="lab status"),
]
