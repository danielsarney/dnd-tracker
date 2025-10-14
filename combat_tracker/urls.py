from django.urls import path
from . import views

app_name = "combat_tracker"

urlpatterns = [
    path("", views.encounter_list_view, name="encounter_list"),
    path("create/", views.encounter_create_view, name="encounter_create"),
    path("<int:pk>/", views.encounter_detail_view, name="encounter_detail"),
    path("<int:pk>/edit/", views.encounter_update_view, name="encounter_update"),
    path("<int:pk>/delete/", views.encounter_delete_view, name="encounter_delete"),
]
