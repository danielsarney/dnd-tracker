from django.urls import path
from . import views

app_name = 'game_sessions'

urlpatterns = [
    path('', views.GameSessionListView.as_view(), name='session_list'),
    path('create/', views.GameSessionCreateView.as_view(), name='session_create'),
    path('<int:pk>/', views.GameSessionDetailView.as_view(), name='session_detail'),
    path('<int:pk>/edit/', views.GameSessionUpdateView.as_view(), name='session_edit'),
    path('<int:pk>/delete/', views.GameSessionDeleteView.as_view(), name='session_delete'),
    path('campaign/<int:campaign_pk>/', views.CampaignSessionsView.as_view(), name='campaign_sessions'),
]
