"""
Main URL Configuration for D&D Tracker Project

This module defines the main URL patterns for the D&D Tracker application.
It includes the root URL redirect and includes all app-specific URL configurations.

URL Structure:
- Root URL (/) redirects to login page
- App URLs are included with prefixes:
  - /accounts/ - User authentication and account management
  - /campaigns/ - D&D campaign management
  - /players/ - Player character management
  - /monsters/ - Monster database management
  - /sessions/ - Game session management
  - /combat/ - Combat encounter tracking
"""

from django.urls import path, include
from django.shortcuts import redirect


def home_redirect(request):
    """
    Redirect root URL to login page.

    This function handles requests to the root URL and redirects
    users to the login page since authentication is required
    for all application features.
    """
    return redirect("accounts:login")


urlpatterns = [
    # Root URL redirects to login
    path("", home_redirect, name="home"),
    # App-specific URL includes
    path("accounts/", include("accounts.urls")),
    path("campaigns/", include("campaigns.urls")),
    path("players/", include("players.urls")),
    path("monsters/", include("monsters.urls")),
    path("sessions/", include("game_sessions.urls")),
    path("combat/", include("combat_tracker.urls")),
]
