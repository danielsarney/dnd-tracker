from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import CombatEncounter, CombatParticipant
from .forms import CombatEncounterForm, CombatParticipantForm
from campaigns.models import Campaign
from characters.models import Character


@login_required
def encounter_list(request):
    """List all combat encounters"""
    encounters = CombatEncounter.objects.select_related('campaign').all().order_by('-created_at')
    
    # Filter by campaign if specified
    campaign_id = request.GET.get('campaign')
    if campaign_id:
        encounters = encounters.filter(campaign_id=campaign_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        from django.db.models import Q
        encounters = encounters.filter(
            Q(name__icontains=search_query) |
            Q(campaign__name__icontains=search_query)
        )
    
    # Get campaigns for filter dropdown
    from campaigns.models import Campaign
    campaigns = Campaign.objects.all().order_by('name')
    
    return render(request, 'initiative/encounter_list.html', {
        'encounters': encounters,
        'campaigns': campaigns,
        'selected_campaign': campaign_id,
        'search_query': search_query
    })


@login_required
def encounter_create(request):
    """Create a new combat encounter"""
    if request.method == 'POST':
        form = CombatEncounterForm(request.POST)
        if form.is_valid():
            encounter = form.save()
            messages.success(request, f'Combat encounter "{encounter.name}" created successfully!')
            return redirect('combat_tracker:encounter_setup', encounter_id=encounter.pk)
    else:
        form = CombatEncounterForm()
    
    # Get all campaigns for the form
    campaigns = Campaign.objects.all().order_by('name')
    
    return render(request, 'initiative/encounter_create.html', {
        'form': form,
        'campaigns': campaigns
    })


@login_required
def encounter_edit(request, encounter_id):
    """Edit a combat encounter"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    
    if request.method == 'POST':
        form = CombatEncounterForm(request.POST, instance=encounter)
        if form.is_valid():
            form.save()
            messages.success(request, f'Combat encounter "{encounter.name}" updated successfully!')
            return redirect('combat_tracker:encounter_detail', encounter_id=encounter.pk)
    else:
        form = CombatEncounterForm(instance=encounter)
    
    # Get all campaigns for the form
    campaigns = Campaign.objects.all().order_by('name')
    
    return render(request, 'initiative/encounter_edit.html', {
        'form': form,
        'encounter': encounter,
        'campaigns': campaigns
    })


@login_required
def encounter_setup(request, encounter_id):
    """Setup participants for a combat encounter"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    participants = encounter.participants.all()
    characters = Character.objects.filter(campaign=encounter.campaign)
    
    if request.method == 'POST':
        form = CombatParticipantForm(request.POST, campaign=encounter.campaign)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.encounter = encounter
            participant.save()
            messages.success(request, f'{participant.name} added to encounter!')
            return redirect('combat_tracker:encounter_setup', encounter_id=encounter.pk)
    else:
        form = CombatParticipantForm(campaign=encounter.campaign)
    
    return render(request, 'initiative/encounter_setup.html', {
        'encounter': encounter,
        'participants': participants,
        'characters': characters,
        'form': form
    })


@login_required
def encounter_detail(request, encounter_id):
    """View and manage an active combat encounter"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    participants = encounter.get_participants()
    current_participant = encounter.get_current_participant()
    
    return render(request, 'initiative/encounter_detail.html', {
        'encounter': encounter,
        'participants': participants,
        'current_participant': current_participant
    })


@login_required
@require_POST
def start_encounter(request, encounter_id):
    """Start a combat encounter"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    
    if encounter.participants.count() == 0:
        messages.error(request, 'Cannot start encounter without participants!')
        return redirect('combat_tracker:encounter_setup', encounter_id=encounter.pk)
    
    encounter.is_active = True
    encounter.current_round = 1
    encounter.current_turn = 0
    encounter.save()
    
    # Reset all participants' turn status
    encounter.participants.update(is_turn_complete=False)
    
    messages.success(request, f'Combat encounter "{encounter.name}" has started!')
    return redirect('combat_tracker:encounter_detail', encounter_id=encounter.pk)


@login_required
@require_POST
def end_turn(request, encounter_id):
    """End the current turn and move to the next"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    
    if not encounter.is_active:
        return JsonResponse({'error': 'Encounter is not active'}, status=400)
    
    current_participant = encounter.get_current_participant()
    if current_participant:
        current_participant.is_turn_complete = True
        current_participant.save()
    
    # Move to next turn
    encounter.next_turn()
    
    return JsonResponse({
        'success': True,
        'current_round': encounter.current_round,
        'current_turn': encounter.current_turn,
        'is_new_round': encounter.current_turn == 0 and encounter.current_round > 1
    })


@login_required
@require_POST
def reset_encounter(request, encounter_id):
    """Reset the encounter to round 1, turn 0"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    encounter.reset_encounter()
    encounter.participants.update(is_turn_complete=False)
    
    messages.success(request, 'Encounter has been reset!')
    return redirect('combat_tracker:encounter_detail', encounter_id=encounter.pk)


@login_required
@require_POST
def remove_participant(request, encounter_id, participant_id):
    """Remove a participant from the encounter"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    participant = get_object_or_404(CombatParticipant, pk=participant_id, encounter=encounter)
    
    participant.delete()
    messages.success(request, f'{participant.name} removed from encounter!')
    return redirect('combat_tracker:encounter_setup', encounter_id=encounter.pk)


@login_required
def encounter_delete(request, encounter_id):
    """Delete a combat encounter"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    
    if request.method == 'POST':
        encounter_name = encounter.name
        encounter.delete()
        messages.success(request, f'Combat encounter "{encounter_name}" deleted successfully!')
        return redirect('combat_tracker:encounter_list')
    
    return render(request, 'initiative/encounter_confirm_delete.html', {'encounter': encounter})