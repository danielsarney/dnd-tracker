from django.urls import path
from . import views

app_name = 'planning'

urlpatterns = [
    path('', views.PlanningSessionListView.as_view(), name='planning_list'),
    path('create/', views.PlanningSessionCreateView.as_view(), name='planning_create'),
    path('<int:pk>/', views.PlanningSessionDetailView.as_view(), name='planning_detail'),
    path('<int:pk>/edit/', views.PlanningSessionUpdateView.as_view(), name='planning_edit'),
    path('<int:pk>/delete/', views.PlanningSessionDeleteView.as_view(), name='planning_delete'),
    path('campaign/<int:campaign_pk>/', views.CampaignPlanningView.as_view(), name='campaign_planning'),
]
