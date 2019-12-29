"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from dashboard import views as dboard_views
from labs import urls as lab_urls

urlpatterns = [
    url(r"^$", dboard_views.index_page, name="index"),
    # Auth
    url(r"^login$", dboard_views.login_page, name="login"),
    url(r"^logout$", dboard_views.logout_page, name="logout"),
    url(r"^signup$", dboard_views.signup_page, name="signup"),
    url(r"^verify-email$", dboard_views.email_verification, name="email verification"),
    # Admin
    url(r"^admin", admin.site.urls),
    # Dashboard
    url(r"^dashboard$", dboard_views.dashboard, name="dashboard"),
    url(r"^labs$", dboard_views.lab_list, name="available labs"),
    url(r"^active-lab$", dboard_views.active_lab, name="active labs"),
    url(r"^settings$", dboard_views.user_settings, name="user settings"),
    url(r"^upload-lab$", dboard_views.upload_lab, name="upload lab"),
    # Lab API
    url(r"^labs/", include(lab_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
