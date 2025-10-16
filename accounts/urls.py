"""
URL Configuration for Accounts App

This module defines URL patterns for user authentication and account management.
It includes routes for user registration, login, logout, two-factor authentication,
and profile management.

URL Patterns:
- Authentication: login, register, logout
- Two-Factor Authentication: verify-2fa, setup-2fa
- Profile Management: profile
"""

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication URLs
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    # Two-Factor Authentication URLs
    path("verify-2fa/", views.verify_2fa_view, name="verify_2fa"),
    path("setup-2fa/", views.setup_2fa_view, name="setup_2fa"),
    # Profile Management URLs
    path("profile/", views.profile_view, name="profile"),
]
