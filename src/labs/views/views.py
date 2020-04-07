import abc
import logging
import os
import requests

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views import View
from django.urls import reverse
from labs.models import LabEnvironment


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
        endpoint = f"{self.api_server_host}/container/{username}"
        # response = requests.put(endpoint)

        # Register new lab with Guacamole
        # TODO: fix SQLi
        with connection.cursor() as cursor:
            query = """
            INSERT INTO guacamole_connection_permission
                (entity_id, connection_id, permission)
            SELECT
                entity_id,
                (
                    SELECT connection_id
                    FROM guacamole_connection
                    WHERE connection_name = "ssh-test"
                ) as connection_id,
                "READ"
            FROM guacamole_entity
            WHERE name = "%s" AND type = "USER";
            """
            self.logger.debug(query)
            cursor.execute(query, [username])

        return self._render_dashboard(request)


class DeleteLabView(HubAPIView):
    def post(self, request):
        username = request.user.username
        endpoint = f"{self.api_server_host}/container/{username}"
        # response = requests.delete(endpoint)
        self.logger.info(f"User {username!r} requested to delete a lab")

        # Delete lab connection from Guacamole
        # TODO: fix SQLi
        with connection.cursor() as cursor:
            query = f"""
            DELETE FROM guacamole_connection_permission
            WHERE (entity_id, connection_id, permission) IN (
                SELECT
                    entity_id,
                    (
                        SELECT connection_id
                        FROM guacamole_connection
                        WHERE connection_name = "ssh-test"
                    ) as connection_id,
                    "READ"
                FROM guacamole_entity
                WHERE name = "%s" and type = "USER"
            )
            """
            self.logger.debug(query)
            cursor.execute(query, [username])

        return self._render_dashboard(request)


class LabStatusView(HubAPIView):
    def post(self, request):
        endpoint = f"{self.api_server_host}/container/{request.user.username}"
        response = requests.get(endpoint)
        return self._render_dashboard(request)
