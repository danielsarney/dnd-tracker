from django.urls import path
from . import views

app_name = "campaigns"

urlpatterns = [
    path("", views.campaign_list_view, name="campaign_list"),
    path("create/", views.campaign_create_view, name="campaign_create"),
    path("<int:pk>/", views.campaign_detail_view, name="campaign_detail"),
    path("<int:pk>/edit/", views.campaign_update_view, name="campaign_update"),
    path("<int:pk>/delete/", views.campaign_delete_view, name="campaign_delete"),
]
