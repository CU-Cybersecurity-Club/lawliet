import os
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from dashboard.forms.auth import SignupForm, LoginForm
from dashboard.forms.settings import PasswordChangeForm
from labs.forms import LabUploadForm
from labs.models import LabEnvironment
from users.models import User, EmailVerificationToken

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


def send_signup_email(email, username, request):
    # When a user tries to sign up with a new email address, we send an
    # email to that user to confirm their email.
    token = EmailVerificationToken.objects.create(email=email, username=username)
    location = f"{reverse('email verification')}?uid={token.uid}"
    url = request.build_absolute_uri(location)
    send_mail(
        "Finish signing up for Lawliet",
        f"Use this link to log in:\n\n{url}",
        settings.EMAIL_HOST_USER,
        [email],
    )


@require_http_methods(["GET"])
def email_verification(request):
    uid = request.GET.get("uid")

    # Redirect if UID isn't specified
    if not uid:
        return redirect(reverse("index"))

    # Redirect if UID doesn't match an existing token
    token = EmailVerificationToken.objects.get(uid=uid)
    if not token:
        return redirect(reverse("index"))

    # Otherwise, activate the user whose email address corresponds
    # to the given token.
    email = token.email
    user = User.objects.get(email=email)
    user.is_active = True
    user.save()

    # Redirect to login
    return redirect("login")


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

            # Create new account. Disable the account until its email address
            # has been verified.
            user = User.objects.create_user(username, email, password, is_active=False)
            send_signup_email(email, username, request)

            context = {"successful_signup": True, "form": SignupForm()}
            return render(request, template, context=context)

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
