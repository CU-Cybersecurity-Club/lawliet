"""
Endpoints for various user-related URLs
"""

from django.conf.urls import url
from users.views import *

urlpatterns = [
    url(r"^info$", UserInfoView.as_view(), name="user_api.user_info"),
]
