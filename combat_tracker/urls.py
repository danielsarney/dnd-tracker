from django.urls import path
from . import views

app_name = "combat_tracker"

urlpatterns = [
    path("", views.encounter_list_view, name="encounter_list"),
    path("create/", views.encounter_create_view, name="encounter_create"),
    path("<int:pk>/", views.encounter_detail_view, name="encounter_detail"),
    path("<int:pk>/edit/", views.encounter_update_view, name="encounter_update"),
    path("<int:pk>/delete/", views.encounter_delete_view, name="encounter_delete"),
    path("<int:pk>/start/", views.start_encounter_view, name="start_encounter"),
    path("<int:pk>/combat/", views.combat_interface_view, name="combat_interface"),
    path("<int:pk>/next-turn/", views.next_turn_view, name="next_turn"),
    path("<int:pk>/end-combat/", views.end_combat_view, name="end_combat"),
    path("<int:pk>/participant/<int:participant_id>/update-hp/", views.update_hp_view, name="update_hp"),
]
