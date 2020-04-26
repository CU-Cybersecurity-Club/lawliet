from django.conf.urls import url
from labs.views import *

urlpatterns = [
    url(r"^generate$", GenerateLabView.as_view(), name="generate lab"),
    url(r"^delete$", DeleteLabView.as_view(), name="delete lab"),
    url(r"^status$", LabStatusView.as_view(), name="lab status"),
]
