import logging
import os
import requests

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from dashboard.forms.settings import PasswordChangeForm
from labs.forms import LabUploadForm
from labs.models import LabEnvironment

TEMPLATES = "dashboard"

"""
---------------------------------------------------
Landing page
---------------------------------------------------
"""


@require_http_methods(["GET"])
def index_page(request):
    return redirect("login")


"""
---------------------------------------------------
Dashboard
---------------------------------------------------
"""


class DashboardView(LoginRequiredMixin, View):

    logger = logging.getLogger("labs")

    def get(self, request):
        template = os.path.join(TEMPLATES, "dashboard.html")
        environments = LabEnvironment.objects.all()
        return render(request, template, context={"environments": environments})

    def post(self, request):
        template = os.path.join(TEMPLATES, "dashboard.html")
        environments = LabEnvironment.objects.all()
        return render(request, template, context={"environments": environments})


@login_required
@require_http_methods(["GET", "POST"])
def user_settings(request):
    template = os.path.join(TEMPLATES, "user_settings.html")
    pass_change_form = PasswordChangeForm(
        request.user, request.POST if request.POST else None
    )

    context = {"password_change_form": pass_change_form}

    if request.POST:
        if (
            "password-change-submit-button" in request.POST
            and pass_change_form.is_valid()
        ):
            new_password = pass_change_form.cleaned_data["new_password"]
            request.user.set_password(new_password)
            request.user.save()

            context["successful_pass_change"] = True

    return render(request, template, context=context)


"""
---------------------------------------------------
Interface for handling lab environments
---------------------------------------------------
"""


@login_required
@require_http_methods(["GET"])
def lab_list(request):
    # List all of the available labs to the user
    template = os.path.join(TEMPLATES, "lab_list.html")
    environments = LabEnvironment.objects.all()
    return render(
        request, template, context={"environments": environments, "lab_menu_show": True}
    )


@login_required
@require_http_methods(["GET"])
def active_lab(request):
    template = os.path.join(TEMPLATES, "active_lab.html")
    return render(request, template, context={"lab_menu_show": True})


@login_required
@user_passes_test(lambda user: user.is_staff)
@require_http_methods(["GET", "POST"])
def upload_lab(request):
    template = os.path.join(TEMPLATES, "lab_upload.html")

    # Construct a LabUploadForm for the page
    lab_form = LabUploadForm(
        request.POST if request.POST else None, request.FILES if request.FILES else None
    )
    context = {"lab_form": lab_form, "lab_menu_show": True}

    if request.POST and lab_form.is_valid():
        lab = lab_form.save()
        context["success"] = True
        context["uploaded_id"] = lab.id

    return render(request, template, context=context)
