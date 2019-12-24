import requests
from django.contrib.auth.decorators import login_required


@login_required
def generate_lab(request):
    api_server_host = f"http://lawliet-k8s-api-server/container/{request.user.username}"
    requests.put(url=api_server_host)
    return redirect("dashboard")


@login_required
def delete_lab(request):
    api_server_host = f"http://lawliet-k8s-api-server/container/{request.user.username}"
    requests.delete(url=api_server_host)
    return redirect("dashboard")
