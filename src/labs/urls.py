from django.conf.urls import url
from labs.views import *

urlpatterns = [
    url(r"^generate$", GenerateLabView.as_view(), name="lab_api.generate"),
    url(r"^delete$", DeleteLabView.as_view(), name="lab_api.delete"),
    url(r"^pod/status", PodStatusView.as_view(), name="lab_api.pod.pod_status"),
    url(r"^list", LabListView.as_view(), name="lab_api.list"),
    url(r"^info$", LabInfoView.as_view(), name="lab_api.info"),
]
