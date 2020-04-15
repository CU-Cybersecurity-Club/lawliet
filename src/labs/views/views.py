import abc
import logging
import os
import requests

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views import View
from django.urls import reverse
from labs.models import LabEnvironment
from guacamole.models import (
    GuacamoleConnection,
    GuacamoleConnectionPermission,
    GuacamoleEntity,
)


class HubAPIView(LoginRequiredMixin, View, metaclass=abc.ABCMeta):
    """
    Abstract parent class for views that require access to the Lawliet Hub
    backend.
    """

    logger = logging.getLogger("labs")
    api_server_host = "http://lawliet-k8s-api-server"

    def _render_dashboard(self, request):
        template = os.path.join("dashboard", "dashboard.html")
        environments = LabEnvironment.objects.all()
        return render(request, template, context={"environments": environments})


class GenerateLabView(HubAPIView):
    def post(self, request):
        username = request.user.username
        self.logger.info(f"User {username!r} requested to create a new lab")
        # response = requests.put(endpoint)
        endpoint = f"{self.api_server_host}/container/{username}"

        # Register new lab with Guacamole
        conn = GuacamoleConnection.objects.get(connection_name="ssh-test")
        user = GuacamoleEntity.objects.get(name=request.user.username, type="USER")
        perm = GuacamoleConnectionPermission.objects.create(
            entity_id=user.entity_id,
            connection_id=conn.connection_id,
            permission="READ",
        )

        return self._render_dashboard(request)


class DeleteLabView(HubAPIView):
    def post(self, request):
        username = request.user.username
        endpoint = f"{self.api_server_host}/container/{username}"
        # response = requests.delete(endpoint)
        self.logger.info(f"User {username!r} requested to delete a lab")

        conn = GuacamoleConnection.objects.get(connection_name="ssh-test")
        user = GuacamoleEntity.objects.get(name=request.user.username, type="USER")
        GuacamoleConnectionPermission.objects.filter(
            entity_id=user.entity_id, connection_id=conn.connection_id
        ).delete()

        return self._render_dashboard(request)


class LabStatusView(HubAPIView):
    def post(self, request):
        endpoint = f"{self.api_server_host}/container/{request.user.username}"
        response = requests.get(endpoint)
        return self._render_dashboard(request)
