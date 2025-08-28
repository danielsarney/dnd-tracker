from django.urls import path
from . import views

app_name = 'characters'

urlpatterns = [
    path('', views.CharacterListView.as_view(), name='character_list'),
    path('create/', views.CharacterCreateView.as_view(), name='character_create'),
    path('<int:pk>/', views.CharacterDetailView.as_view(), name='character_detail'),
    path('<int:pk>/edit/', views.CharacterUpdateView.as_view(), name='character_edit'),
    path('<int:pk>/delete/', views.CharacterDeleteView.as_view(), name='character_delete'),
    path('campaign/<int:campaign_pk>/', views.CampaignCharactersView.as_view(), name='campaign_characters'),
]
