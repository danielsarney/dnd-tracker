from django.urls import path
from . import views

app_name = "monsters"

urlpatterns = [
    path("", views.monster_list_view, name="monster_list"),
    path("create/", views.monster_create_view, name="monster_create"),
    path("<int:pk>/", views.monster_detail_view, name="monster_detail"),
    path("<int:pk>/edit/", views.monster_update_view, name="monster_update"),
    path("<int:pk>/delete/", views.monster_delete_view, name="monster_delete"),
]
