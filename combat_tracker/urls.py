"""
URL Configuration for Combat Tracker App

This module defines URL patterns for D&D combat encounter management.
It includes routes for encounter CRUD operations and combat session management.

URL Patterns:
- Encounter Management: /, /create/, /<id>/, /<id>/edit/, /<id>/delete/
- Combat Session Management: /<id>/start/, /<id>/combat/, /<id>/next-turn/, /<id>/end-combat/
- Hit Point Tracking: /<id>/participant/<participant_id>/update-hp/
"""

from django.urls import path
from . import views

app_name = "combat_tracker"

urlpatterns = [
    # Encounter management URLs
    path("", views.encounter_list_view, name="encounter_list"),
    path("create/", views.encounter_create_view, name="encounter_create"),
    path("<int:pk>/", views.encounter_detail_view, name="encounter_detail"),
    path("<int:pk>/edit/", views.encounter_update_view, name="encounter_update"),
    path("<int:pk>/delete/", views.encounter_delete_view, name="encounter_delete"),
    # Combat session management URLs
    path("<int:pk>/start/", views.start_encounter_view, name="start_encounter"),
    path("<int:pk>/combat/", views.combat_interface_view, name="combat_interface"),
    path("<int:pk>/next-turn/", views.next_turn_view, name="next_turn"),
    path("<int:pk>/end-combat/", views.end_combat_view, name="end_combat"),
    # Hit point tracking URL
    path(
        "<int:pk>/participant/<int:participant_id>/update-hp/",
        views.update_hp_view,
        name="update_hp",
    ),
]
