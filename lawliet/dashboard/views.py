import os
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from dashboard.forms.auth import SignupForm, LoginForm
from dashboard.forms.settings import PasswordChangeForm
from dashboard.models import LabEnvironment

TEMPLATES = "dashboard"

"""
---------------------------------------------------
Landing page
---------------------------------------------------
"""


def index_page(request):
    return redirect("/login")


"""
---------------------------------------------------
Authentication
---------------------------------------------------
"""


def login_page(request):
    if request.user.is_authenticated:
        return redirect("/dashboard")

    # On a POST request, attempt to login
    form = LoginForm(request.POST if request.POST else None)
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            redirect_url = request.GET.get("next", "/dashboard")
            return redirect(redirect_url)

    template = os.path.join(TEMPLATES, "login.html")
    return render(request, template, context={"form": form})


def signup_page(request):
    if request.user.is_authenticated:
        return redirect("/dashboard")

    template = os.path.join(TEMPLATES, "signup.html")

    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            # TODO: send verification email
            email = form.cleaned_data.get("email")
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = User.objects.create_user(username, email, password)
            return redirect("/dashboard")

        else:
            return render(request, template, context={"form": form})

    else:
        return render(request, template, context={"form": SignupForm()})


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect("/login")


"""
---------------------------------------------------
Dashboard
---------------------------------------------------
"""


@login_required
def dashboard(request):
    template = os.path.join(TEMPLATES, "dashboard.html")
    return render(request, template)


@login_required
def lab_list(request):
    # List all of the available labs to the user
    template = os.path.join(TEMPLATES, "lab_list.html")
    environments = LabEnvironment.objects.all()
    return render(request, template, context={"environments": environments})


@login_required
def active_lab(request):
    template = os.path.join(TEMPLATES, "active_lab.html")
    return render(request, template)


@login_required
def scoreboard(request):
    template = os.path.join(TEMPLATES, "scoreboard.html")
    return render(request, template)


@login_required
def user_settings(request):
    template = os.path.join(TEMPLATES, "user_settings.html")
    password_change_form = PasswordChangeForm()
    return render(
        request, template, context={"password_change_form": password_change_form}
    )


@login_required
def generate_lab(request):
    api_server_host = f"http://lawliet-k8s-api-server/container/{request.user.username}"
    requests.put(url=api_server_host)
    return redirect("/dashboard")


@login_required
def delete_lab(request):
    api_server_host = f"http://lawliet-k8s-api-server/container/{request.user.username}"
    requests.delete(url=api_server_host)
    return redirect("/dashboard")
