from django.urls import path
from . import views

app_name = "players"

urlpatterns = [
    path("", views.player_list_view, name="player_list"),
    path("create/", views.player_create_view, name="player_create"),
    path("<int:pk>/", views.player_detail_view, name="player_detail"),
    path("<int:pk>/edit/", views.player_update_view, name="player_update"),
    path("<int:pk>/delete/", views.player_delete_view, name="player_delete"),
]
