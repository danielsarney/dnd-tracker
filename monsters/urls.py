from django.urls import path
from . import views

app_name = 'monsters'

urlpatterns = [
    path('', views.MonsterListView.as_view(), name='monster_list'),
    path('create/', views.MonsterCreateView.as_view(), name='monster_create'),
    path('<int:pk>/', views.MonsterDetailView.as_view(), name='monster_detail'),
    path('<int:pk>/edit/', views.MonsterUpdateView.as_view(), name='monster_edit'),
    path('<int:pk>/delete/', views.MonsterDeleteView.as_view(), name='monster_delete'),
]
