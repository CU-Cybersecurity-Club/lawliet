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
    GuacamoleConnectionParameter,
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

        # Get the lab environment specified by the "create" parameter in
        # the URL
        lab_id = request.GET.get("create", None)
        labenv = LabEnvironment.objects.filter(id=lab_id)

        if not labenv.exists():
            self.logger.info(
                (
                    f"User {username!r} failed to create new lab environment: lab "
                    f"with id {lab_id} does not exist"
                )
            )
        else:
            protocol = labenv[0].protocol
            port = str(labenv[0].port)

            # Create a new GuacamoleConnection to the container
            conn = GuacamoleConnection.objects.create(
                connection_name="ssh-test", protocol=protocol,
            )
            GuacamoleConnectionParameter.objects.bulk_create(
                [
                    GuacamoleConnectionParameter(
                        connection=conn,
                        parameter_name="hostname",
                        parameter_value="lawliet-ssh",
                    ),
                    GuacamoleConnectionParameter(
                        connection=conn, parameter_name="port", parameter_value=port,
                    ),
                ]
            )

            # Give the user permission to connect to the container
            entity = GuacamoleEntity.objects.get(
                name=request.user.username, type="USER"
            )
            perm = GuacamoleConnectionPermission.objects.create(
                entity=entity, connection=conn, permission="READ",
            )

        return self._render_dashboard(request)


class DeleteLabView(HubAPIView):
    def post(self, request):
        username = request.user.username
        endpoint = f"{self.api_server_host}/container/{username}"
        # response = requests.delete(endpoint)
        self.logger.info(f"User {username!r} requested to delete a lab")

        conn = GuacamoleConnection.objects.get(connection_name="ssh-test")

        # Delete the connection
        conn.delete()

        return self._render_dashboard(request)


class LabStatusView(HubAPIView):
    def post(self, request):
        endpoint = f"{self.api_server_host}/container/{request.user.username}"
        response = requests.get(endpoint)
        return self._render_dashboard(request)
