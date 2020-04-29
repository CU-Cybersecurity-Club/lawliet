"""
API for accessing user information
"""

import abc
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View


class UserAPIView(LoginRequiredMixin, View, metaclass=abc.ABCMeta):
    """
    Abstract parent class for views that build the user REST API.
    """

    pass


class UserInfoView(UserAPIView):
    """
    GET endpoint for retrieving user information.
    """

    def get(self, request):
        user = request.user
        info = {
            "username": user.username,
            "email": user.email,
            "date_joined": user.date_joined,
            "n_active_labs": user.n_active_labs,
        }

        return JsonResponse(info)
