from django.urls import path
from . import views

app_name = "game_sessions"

urlpatterns = [
    path("", views.session_list_view, name="session_list"),
    path("create/", views.session_create_view, name="session_create"),
    path("<int:pk>/", views.session_detail_view, name="session_detail"),
    path("<int:pk>/edit/", views.session_update_view, name="session_update"),
    path("<int:pk>/delete/", views.session_delete_view, name="session_delete"),
]
