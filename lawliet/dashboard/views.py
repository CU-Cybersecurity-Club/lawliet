import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods

from dashboard.forms.auth import SignupForm, LoginForm
from dashboard.forms.settings import PasswordChangeForm
from dashboard.forms.labs import LabUploadForm
from labs.models import LabEnvironment
from users.models import User

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
Authentication
---------------------------------------------------
"""


@require_http_methods(["GET", "POST"])
def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    # On a POST request, attempt to login
    form = LoginForm(request.POST if request.POST else None)
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            redirect_url = request.GET.get("next", "dashboard")
            return redirect(redirect_url)

    template = os.path.join(TEMPLATES, "login.html")
    return render(request, template, context={"form": form})


@require_http_methods(["GET", "POST"])
def signup_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    template = os.path.join(TEMPLATES, "signup.html")

    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            # TODO: send verification email
            email = form.cleaned_data.get("email")
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = User.objects.create_user(username, email, password)
            return redirect("dashboard")

        else:
            return render(request, template, context={"form": form})

    else:
        return render(request, template, context={"form": SignupForm()})


@require_http_methods(["GET"])
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect("login")


"""
---------------------------------------------------
Dashboard
---------------------------------------------------
"""


@login_required
@require_http_methods(["GET"])
def dashboard(request):
    template = os.path.join(TEMPLATES, "dashboard.html")
    return render(request, template)


@login_required
@require_http_methods(["GET", "POST"])
def user_settings(request):
    template = os.path.join(TEMPLATES, "user_settings.html")
    pass_change_form = PasswordChangeForm(
        request.user, request.POST if request.POST else None
    )

    context = {"password_change_form": pass_change_form}

    if request.POST:

        if request.POST.get("password-change-submit-button"):
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
        request.user,
        request.POST if request.POST else None,
        request.FILES if request.FILES else None,
    )
    context = {"lab_form": lab_form, "lab_menu_show": True}

    if request.POST and lab_form.is_valid():
        lab = lab_form.save()
        context["success"] = True
        context["uploaded_id"] = lab.id

    return render(request, template, context=context)
