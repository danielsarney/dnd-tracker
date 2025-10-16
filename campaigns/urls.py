"""
URL Configuration for Campaigns App

This module defines URL patterns for D&D campaign management.
It includes routes for campaign CRUD operations (Create, Read, Update, Delete).

URL Patterns:
- Campaign List: / (root)
- Campaign Create: /create/
- Campaign Detail: /<id>/
- Campaign Update: /<id>/edit/
- Campaign Delete: /<id>/delete/
"""

from django.urls import path
from . import views

app_name = "campaigns"

urlpatterns = [
    # Campaign management URLs
    path("", views.campaign_list_view, name="campaign_list"),
    path("create/", views.campaign_create_view, name="campaign_create"),
    path("<int:pk>/", views.campaign_detail_view, name="campaign_detail"),
    path("<int:pk>/edit/", views.campaign_update_view, name="campaign_update"),
    path("<int:pk>/delete/", views.campaign_delete_view, name="campaign_delete"),
]
