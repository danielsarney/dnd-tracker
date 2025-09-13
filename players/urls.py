from django.urls import path
from . import views

app_name = 'players'

urlpatterns = [
    path('', views.PlayerListView.as_view(), name='player_list'),
    path('create/', views.PlayerCreateView.as_view(), name='player_create'),
    path('<int:pk>/', views.PlayerDetailView.as_view(), name='player_detail'),
    path('<int:pk>/edit/', views.PlayerUpdateView.as_view(), name='player_edit'),
    path('<int:pk>/delete/', views.PlayerDeleteView.as_view(), name='player_delete'),
    path('campaign/<int:campaign_pk>/', views.CampaignPlayersView.as_view(), name='campaign_players'),
]
