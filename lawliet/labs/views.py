import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse


@login_required
def generate_lab(request):
    # api_server_host = f"http://lawliet-k8s-api-server/container/{request.user.username}"
    # requests.put(url=api_server_host)
    # return redirect("dashboard")
    response = {"created": False, "error": "TODO"}
    return JsonResponse(response)


@login_required
def delete_lab(request):
    # api_server_host = f"http://lawliet-k8s-api-server/container/{request.user.username}"
    # requests.delete(url=api_server_host)
    # return redirect("dashboard")
    response = {"deleted": False, "error": "TODO"}
    return JsonResponse(response)


@login_required
def lab_status(request):
    # TODO: display the actual status of the currently running labs
    return JsonResponse({"labs": []})
