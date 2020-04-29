import abc
import logging
import os
import requests

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
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

    def generate_response(self, status=200, **kwargs):
        """
        Return a JsonResponse with the given status code, and with contents given
        by the keyword arguments.
        """
        self.logger.info(f"status = {status}")
        self.logger.info(f"kwargs = {kwargs}")
        return JsonResponse(kwargs, status=status)


class GenerateLabView(HubAPIView):
    def post(self, request):
        username = request.user.username
        env_id = request.GET.get("create", "")

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
            return self.generate_response(
                status=422, err=f"Lab environment does not exist", id=lab_id,
            )
        else:
            image = labenv[0].url
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

            try:
                msg = f"Username {username!r} requested to create a new lab (environment id: {env_id})"
                msg += f" (image: {image}) (port: {port})"
                self.logger.info(msg)
                endpoint = f"{self.api_server_host}/pods/{username}"
                response = requests.put(
                    endpoint, json={"image": image, "ports": [port]}
                )
            except Exception as ex:
                self.logger.error(f"API error creating lab: {ex}")

            # Increment the number of active labs that the user has
            request.user.n_active_labs += 1
            request.user.save()

            return self.generate_response(
                status=200,
                msg="Successfully created lab",
                id=lab_id,
                protocol=protocol,
                port=port,
            )


class DeleteLabView(HubAPIView):
    def post(self, request):
        username = request.user.username
        endpoint = f"{self.api_server_host}/pods/{username}"
        try:
            response = requests.delete(endpoint)
        except Exception as ex:
            self.logger.error(f"API error deleting lab: {ex}")
        self.logger.info(f"User {username!r} requested to delete a lab")

        conn = GuacamoleConnection.objects.filter(connection_name="ssh-test")
        n_connections = len(conn)

        # Decrement the number of active labs that the user has
        if request.user.n_active_labs > 0:
            request.user.n_active_labs -= 1
            request.user.save()

        # Delete the connection
        conn.delete()

        return self.generate_response(
            status=200, msg="Successfully deleted labs", n_deleted=n_connections,
        )


class LabStatusView(HubAPIView):
    def post(self, request):
        endpoint = f"{self.api_server_host}/pods/{request.user.username}"
        response = requests.get(endpoint)
        return self._render_dashboard(request)
