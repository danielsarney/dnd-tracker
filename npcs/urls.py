from django.urls import path
from . import views

app_name = 'npcs'

urlpatterns = [
    path('', views.NPCListView.as_view(), name='npc_list'),
    path('create/', views.NPCCreateView.as_view(), name='npc_create'),
    path('<int:pk>/', views.NPCDetailView.as_view(), name='npc_detail'),
    path('<int:pk>/edit/', views.NPCUpdateView.as_view(), name='npc_edit'),
    path('<int:pk>/delete/', views.NPCDeleteView.as_view(), name='npc_delete'),
    path('campaign/<int:campaign_pk>/', views.CampaignNPCsView.as_view(), name='campaign_npcs'),
]
