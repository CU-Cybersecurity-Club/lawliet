"""
Views related to the User model and authentication.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from users.forms import SignupForm, LoginForm
from users.models import User, EmailVerificationToken

"""
---------------------------------------------------
Helper functions
---------------------------------------------------
"""


def send_signup_email(email, username, request):
    # When a user tries to sign up with a new email address, we send an
    # email to that user to confirm their email.
    token = EmailVerificationToken.objects.create(email=email, username=username)
    url = request.build_absolute_uri(token.email_verification_location)
    send_mail(
        "Finish signing up for Lawliet",
        f"Use this link to log in:\n\n{url}",
        settings.EMAIL_HOST_USER,
        [email],
    )


"""
---------------------------------------------------
Authentication
---------------------------------------------------
"""


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

    return render(request, "login.html", context={"form": form})


@require_http_methods(["GET", "POST"])
def signup_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    template = "signup.html"

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
