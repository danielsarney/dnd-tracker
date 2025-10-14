from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.contrib import messages
import re
from .models import Encounter, CombatSession, CombatParticipant
from .forms import EncounterForm, InitiativeForm, HPTrackingForm


def parse_monster_hp(hp_string):
    """Extract numeric HP value from monster HP string like '82 (10d11 + 26)'"""
    if not hp_string:
        return 0
    
    # Try to extract the first number from the string
    match = re.match(r'(\d+)', str(hp_string).strip())
    if match:
        return int(match.group(1))
    
    return 0


@login_required
def encounter_list_view(request):
    """Display list of encounters with search functionality"""
    encounters = Encounter.objects.all()

    # Handle search functionality
    search_query = request.GET.get("search")
    if search_query:
        encounters = encounters.filter(
            models.Q(name__icontains=search_query)
            | models.Q(description__icontains=search_query)
            | models.Q(campaign__title__icontains=search_query)
        )

    return render(
        request,
        "combat_tracker/encounter_list.html",
        {"encounters": encounters, "search_query": search_query},
    )


@login_required
def encounter_detail_view(request, pk):
    """Display encounter details with player and monster stats"""
    encounter = get_object_or_404(Encounter, pk=pk)
    return render(request, "combat_tracker/encounter_detail.html", {"encounter": encounter})


@login_required
def encounter_create_view(request):
    """Create a new encounter"""
    if request.method == "POST":
        form = EncounterForm(request.POST)
        if form.is_valid():
            encounter = form.save()
            return redirect("combat_tracker:encounter_detail", pk=encounter.pk)
    else:
        form = EncounterForm()

    return render(request, "combat_tracker/encounter_create.html", {"form": form})


@login_required
def encounter_update_view(request, pk):
    """Update an existing encounter"""
    encounter = get_object_or_404(Encounter, pk=pk)

    if request.method == "POST":
        form = EncounterForm(request.POST, instance=encounter)
        if form.is_valid():
            form.save()
            return redirect("combat_tracker:encounter_detail", pk=pk)
    else:
        form = EncounterForm(instance=encounter)

    return render(
        request, "combat_tracker/encounter_update.html", {"form": form, "encounter": encounter}
    )


@login_required
def encounter_delete_view(request, pk):
    """Delete an encounter"""
    encounter = get_object_or_404(Encounter, pk=pk)

    if request.method == "POST":
        encounter.delete()
        return redirect("combat_tracker:encounter_list")

    return render(request, "combat_tracker/encounter_delete.html", {"encounter": encounter})


@login_required
def start_encounter_view(request, pk):
    """Start an encounter by entering initiative rolls"""
    encounter = get_object_or_404(Encounter, pk=pk)
    
    # Check if combat session already exists
    if hasattr(encounter, 'combat_session'):
        messages.info(request, "This encounter is already in combat!")
        return redirect("combat_tracker:combat_interface", pk=pk)
    
    if request.method == "POST":
        form = InitiativeForm(encounter, request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create combat session
                combat_session = CombatSession.objects.create(encounter=encounter)
                
                # Create combat participants for players
                for player in encounter.players.all():
                    field_name = f"player_{player.id}_initiative"
                    initiative = form.cleaned_data[field_name]
                    CombatParticipant.objects.create(
                        combat_session=combat_session,
                        participant_type='player',
                        player=player,
                        initiative=initiative,
                        current_hp=0,  # Players manage their own HP
                        max_hp=0      # Players manage their own HP
                    )
                
                # Create combat participants for monsters
                for monster in encounter.monsters.all():
                    field_name = f"monster_{monster.id}_initiative"
                    initiative = form.cleaned_data[field_name]
                    monster_hp = parse_monster_hp(monster.hp)
                    CombatParticipant.objects.create(
                        combat_session=combat_session,
                        participant_type='monster',
                        monster=monster,
                        initiative=initiative,
                        current_hp=monster_hp,
                        max_hp=monster_hp
                    )
                
                messages.success(request, "Combat started! Initiative order has been set.")
                return redirect("combat_tracker:combat_interface", pk=pk)
    else:
        form = InitiativeForm(encounter)
    
    return render(request, "combat_tracker/start_encounter.html", {
        "encounter": encounter,
        "form": form
    })


@login_required
def combat_interface_view(request, pk):
    """Main combat interface showing current turn and participant details"""
    encounter = get_object_or_404(Encounter, pk=pk)
    combat_session = get_object_or_404(CombatSession, encounter=encounter)
    
    # Get all participants for display (including dead ones)
    all_participants = combat_session.participants.all().order_by('-initiative')
    
    # Get only alive participants for turn sequence
    alive_participants = combat_session.participants.filter(is_dead=False).order_by('-initiative')
    
    if not alive_participants.exists():
        messages.warning(request, "No active participants in combat!")
        return redirect("combat_tracker:encounter_detail", pk=pk)
    
    # Get current turn participant from alive participants only
    current_turn_index = combat_session.current_turn_index
    if current_turn_index >= alive_participants.count():
        current_turn_index = 0
        combat_session.current_turn_index = 0
        combat_session.current_round += 1
        combat_session.save()
    
    current_participant = alive_participants[current_turn_index] if alive_participants.exists() else None
    
    return render(request, "combat_tracker/combat_interface.html", {
        "encounter": encounter,
        "combat_session": combat_session,
        "all_participants": all_participants,
        "alive_participants": alive_participants,
        "current_participant": current_participant,
        "current_turn_index": current_turn_index
    })


@login_required
def next_turn_view(request, pk):
    """Move to the next turn in combat"""
    encounter = get_object_or_404(Encounter, pk=pk)
    combat_session = get_object_or_404(CombatSession, encounter=encounter)
    
    # Only work with alive participants
    alive_participants = combat_session.participants.filter(is_dead=False).order_by('-initiative')
    
    if alive_participants.exists():
        # Mark current turn as completed
        current_participant = alive_participants[combat_session.current_turn_index]
        current_participant.turn_completed = True
        current_participant.save()
        
        # Move to next turn
        combat_session.current_turn_index += 1
        
        # If we've gone through all alive participants, start new round
        if combat_session.current_turn_index >= alive_participants.count():
            combat_session.current_turn_index = 0
            combat_session.current_round += 1
            # Reset all turn completed flags for new round
            alive_participants.update(turn_completed=False)
        
        combat_session.save()
        
        messages.success(request, f"Turn completed! Round {combat_session.current_round}")
    
    return redirect("combat_tracker:combat_interface", pk=pk)


@login_required
def end_combat_view(request, pk):
    """End the current combat session"""
    encounter = get_object_or_404(Encounter, pk=pk)
    combat_session = get_object_or_404(CombatSession, encounter=encounter)
    
    if request.method == "POST":
        combat_session.is_active = False
        combat_session.save()
        messages.success(request, "Combat has ended!")
        return redirect("combat_tracker:encounter_detail", pk=pk)
    
    return render(request, "combat_tracker/end_combat.html", {
        "encounter": encounter,
        "combat_session": combat_session
    })


@login_required
def update_hp_view(request, pk, participant_id):
    """Update HP for a combat participant (damage/healing)"""
    encounter = get_object_or_404(Encounter, pk=pk)
    combat_session = get_object_or_404(CombatSession, encounter=encounter)
    participant = get_object_or_404(CombatParticipant, pk=participant_id, combat_session=combat_session)
    
    if request.method == "POST":
        form = HPTrackingForm(request.POST)
        if form.is_valid():
            change_type = form.cleaned_data['change_type']
            amount = form.cleaned_data['amount']
            notes = form.cleaned_data.get('notes', '')
            
            if change_type == 'damage':
                participant.current_hp -= amount
                if participant.current_hp <= 0:
                    participant.current_hp = 0
                    participant.is_dead = True
                    messages.success(request, f"{participant.name} takes {amount} damage and is now dead!")
                else:
                    messages.success(request, f"{participant.name} takes {amount} damage. Current HP: {participant.current_hp}")
            else:  # healing
                participant.current_hp += amount
                if participant.current_hp > participant.max_hp:
                    participant.current_hp = participant.max_hp
                participant.is_dead = False  # Revive if they were dead
                messages.success(request, f"{participant.name} is healed for {amount} HP. Current HP: {participant.current_hp}")
            
            participant.save()
            return redirect("combat_tracker:combat_interface", pk=pk)
    else:
        form = HPTrackingForm()
    
    return render(request, "combat_tracker/update_hp.html", {
        "encounter": encounter,
        "combat_session": combat_session,
        "participant": participant,
        "form": form
    })
