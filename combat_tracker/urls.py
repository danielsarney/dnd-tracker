from django.urls import path
from . import views

app_name = 'combat_tracker'

urlpatterns = [
    path('', views.encounter_list, name='encounter_list'),
    path('create/', views.encounter_create, name='encounter_create'),
    path('edit/<int:encounter_id>/', views.encounter_edit, name='encounter_edit'),
    path('setup/<int:encounter_id>/', views.encounter_setup, name='encounter_setup'),
    path('detail/<int:encounter_id>/', views.encounter_detail, name='encounter_detail'),
    path('start/<int:encounter_id>/', views.start_encounter, name='start_encounter'),
    path('end-turn/<int:encounter_id>/', views.end_turn, name='end_turn'),
    path('reset/<int:encounter_id>/', views.reset_encounter, name='reset_encounter'),
    path('remove-participant/<int:encounter_id>/<int:participant_id>/', views.remove_participant, name='remove_participant'),
    path('delete/<int:encounter_id>/', views.encounter_delete, name='encounter_delete'),
    # Combat modification endpoints
    path('modify-hp/<int:encounter_id>/<int:participant_id>/', views.modify_hit_points, name='modify_hit_points'),
    path('modify-ac/<int:encounter_id>/<int:participant_id>/', views.modify_armor_class, name='modify_armor_class'),
    path('apply-damage/<int:encounter_id>/<int:participant_id>/', views.apply_damage, name='apply_damage'),
    path('apply-healing/<int:encounter_id>/<int:participant_id>/', views.apply_healing, name='apply_healing'),
]
