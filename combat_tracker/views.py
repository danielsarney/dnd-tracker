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


@login_required
def encounter_list(request):
    """List all combat encounters"""
    encounters = CombatEncounter.objects.select_related('campaign').all().order_by('-created_at')
    
    # Filter by campaign if specified
    campaign_id = request.GET.get('campaign')
    if campaign_id:
        encounters = encounters.filter(campaign_id=campaign_id)
    
    # Filter by encounter name if specified
    encounter_name = request.GET.get('encounter_name')
    if encounter_name:
        encounters = encounters.filter(name=encounter_name)
    
    # Get campaigns for filter dropdown
    from campaigns.models import Campaign
    campaigns = Campaign.objects.all().order_by('name')
    
    # Get all encounters for the encounter name dropdown
    all_encounters = CombatEncounter.objects.all().order_by('name').distinct('name')
    
    return render(request, 'initiative/encounter_list.html', {
        'encounters': encounters,
        'campaigns': campaigns,
        'all_encounters': all_encounters,
        'selected_campaign': campaign_id,
        'selected_encounter_name': encounter_name
    })


@login_required
def encounter_create(request):
    """Create a new combat encounter"""
    if request.method == 'POST':
        form = CombatEncounterForm(request.POST)
        if form.is_valid():
            encounter = form.save()
            messages.success(request, f'Combat encounter "{encounter.name}" created successfully!')
            return redirect('combat_tracker:encounter_detail', encounter_id=encounter.pk)
    else:
        form = CombatEncounterForm()
    
    return render(request, 'initiative/encounter_create.html', {'form': form})


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
def encounter_detail(request, encounter_id):
    """View and manage an active combat encounter"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    participants = encounter.get_participants()
    living_participants = encounter.get_living_participants()
    current_participant = encounter.get_current_participant()
    
    # Get character data for dropdowns
    from players.models import Player
    from npcs.models import NPC
    from monsters.models import Monster
    
    # Handle participant form submission
    if request.method == 'POST' and 'character_type' in request.POST:
        # Debug: print form data and available players
        print("Form data:", request.POST)
        print("Encounter campaign:", encounter.campaign)
        available_players = Player.objects.filter(campaign=encounter.campaign)
        print("Available players:", [p.pk for p in available_players])
        
        form = CombatParticipantForm(request.POST, campaign=encounter.campaign)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.encounter = encounter
            
            # Populate stats from character if selected
            if participant.player or participant.npc or participant.monster:
                participant.populate_from_character()
            
            participant.save()
            
            # If combat is active, adjust current turn if new participant has higher initiative
            if encounter.is_active:
                # Get all participants ordered by initiative (highest first)
                all_participants = encounter.get_participants()
                new_participant_position = 0
                
                # Find where the new participant should be in the initiative order
                for i, existing_participant in enumerate(all_participants):
                    if existing_participant.initiative_roll < participant.initiative_roll:
                        new_participant_position = i
                        break
                    elif existing_participant.initiative_roll == participant.initiative_roll:
                        # Same initiative - new participant goes after (lower in list)
                        new_participant_position = i + 1
                    else:
                        new_participant_position = i + 1
                
                # If the new participant is inserted before the current turn, adjust current_turn
                if new_participant_position <= encounter.current_turn:
                    encounter.current_turn += 1
                    encounter.save()
                
                messages.success(request, f'{participant.name} added to encounter and inserted into initiative order!')
            else:
                messages.success(request, f'{participant.name} added to encounter!')
            
            return redirect('combat_tracker:encounter_detail', encounter_id=encounter.pk)
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CombatParticipantForm(campaign=encounter.campaign)
    
    # Get character data for dropdowns
    players = Player.objects.all()
    npcs = NPC.objects.all()
    monsters = Monster.objects.all()
    
    return render(request, 'initiative/encounter_detail.html', {
        'encounter': encounter,
        'participants': participants,
        'living_participants': living_participants,
        'current_participant': current_participant,
        'participant_form': form,
        'players': players,
        'npcs': npcs,
        'monsters': monsters
    })


@login_required
@require_POST
def start_encounter(request, encounter_id):
    """Start a combat encounter"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    
    if encounter.participants.count() == 0:
        messages.error(request, 'Cannot start encounter without participants!')
        return redirect('combat_tracker:encounter_create_edit', encounter_id=encounter.pk)
    
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
    return redirect('combat_tracker:encounter_create_edit', encounter_id=encounter.pk)


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


@login_required
@require_POST
def modify_hit_points(request, encounter_id, participant_id):
    """Modify a participant's hit points during combat"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    participant = get_object_or_404(CombatParticipant, pk=participant_id, encounter=encounter)
    
    try:
        data = json.loads(request.body)
        new_hp = int(data.get('hit_points', 0))
        
        participant.hit_points = new_hp
        
        # Check for death
        if new_hp <= 0:
            participant.is_dead = True
        else:
            participant.is_dead = False
            
        participant.save()
        
        return JsonResponse({
            'success': True,
            'hit_points': participant.hit_points,
            'is_dead': participant.is_dead,
            'is_alive': participant.is_alive()
        })
    except (ValueError, KeyError) as e:
        return JsonResponse({'error': 'Invalid data'}, status=400)


@login_required
@require_POST
def modify_armor_class(request, encounter_id, participant_id):
    """Modify a participant's armor class during combat"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    participant = get_object_or_404(CombatParticipant, pk=participant_id, encounter=encounter)
    
    try:
        data = json.loads(request.body)
        new_ac = int(data.get('armor_class', 10))
        
        participant.armor_class = new_ac
        participant.save()
        
        return JsonResponse({
            'success': True,
            'armor_class': participant.armor_class
        })
    except (ValueError, KeyError) as e:
        return JsonResponse({'error': 'Invalid data'}, status=400)


@login_required
@require_POST
def apply_damage(request, encounter_id, participant_id):
    """Apply damage to a participant"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    participant = get_object_or_404(CombatParticipant, pk=participant_id, encounter=encounter)
    
    try:
        data = json.loads(request.body)
        damage = int(data.get('damage', 0))
        
        died = participant.take_damage(damage)
        
        return JsonResponse({
            'success': True,
            'hit_points': participant.hit_points,
            'is_dead': participant.is_dead,
            'is_alive': participant.is_alive(),
            'died': died
        })
    except (ValueError, KeyError) as e:
        return JsonResponse({'error': 'Invalid data'}, status=400)


@login_required
@require_POST
def apply_healing(request, encounter_id, participant_id):
    """Apply healing to a participant"""
    encounter = get_object_or_404(CombatEncounter, pk=encounter_id)
    participant = get_object_or_404(CombatParticipant, pk=participant_id, encounter=encounter)
    
    try:
        data = json.loads(request.body)
        healing = int(data.get('healing', 0))
        
        participant.heal(healing)
        
        return JsonResponse({
            'success': True,
            'hit_points': participant.hit_points,
            'is_dead': participant.is_dead,
            'is_alive': participant.is_alive()
        })
    except (ValueError, KeyError) as e:
        return JsonResponse({'error': 'Invalid data'}, status=400)