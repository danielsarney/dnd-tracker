from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.CampaignListView.as_view(), name='campaign_list'),
    path('create/', views.CampaignCreateView.as_view(), name='campaign_create'),
    path('<int:pk>/', views.CampaignDetailView.as_view(), name='campaign_detail'),
    path('<int:pk>/edit/', views.CampaignUpdateView.as_view(), name='campaign_edit'),
    path('<int:pk>/delete/', views.CampaignDeleteView.as_view(), name='campaign_delete'),
]
