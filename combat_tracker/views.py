"""
Combat Tracker Views for D&D Tracker

This module contains all the view functions for combat encounter management.
It handles encounter CRUD operations, combat session management, initiative
tracking, turn management, and hit point tracking during combat.

Key Features:
- Encounter creation and management
- Combat session initialization with initiative rolls
- Turn-based combat tracking
- Hit point management (damage/healing)
- Combat interface with initiative order
- Combat session termination
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.contrib import messages
import re
from .models import Encounter, CombatSession, CombatParticipant
from .forms import EncounterForm, InitiativeForm, HPTrackingForm


def parse_monster_hp(hp_string):
    """
    Extract numeric HP value from monster HP string.

    Monster HP is stored as strings like '82 (10d11 + 26)' where the first
    number represents the average hit points. This function extracts that
    numeric value for combat calculations.

    Args:
        hp_string (str): HP string from monster data

    Returns:
        int: Numeric HP value, or 0 if parsing fails
    """
    if not hp_string:
        return 0

    # Extract the first number from the HP string
    match = re.match(r"(\d+)", str(hp_string).strip())
    if match:
        return int(match.group(1))

    return 0


@login_required
def encounter_list_view(request):
    """
    Display a list of all encounters with optional search functionality.

    This view shows all encounters in the system and allows users to search
    through encounter names, descriptions, and associated campaigns using
    a search query parameter.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered encounter list page with search results
    """
    encounters = Encounter.objects.all()

    # Handle search functionality across multiple encounter fields
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
    """
    Display detailed information about a specific encounter.

    This view shows all the details of an encounter including its name,
    description, associated campaign, participating players, and monsters.

    Args:
        request: HTTP request object
        pk: Primary key of the encounter to display

    Returns:
        HttpResponse: Rendered encounter detail page
    """
    encounter = get_object_or_404(Encounter, pk=pk)
    return render(
        request, "combat_tracker/encounter_detail.html", {"encounter": encounter}
    )


@login_required
def encounter_create_view(request):
    """
    Handle creation of new encounters.

    This view processes encounter creation forms and creates new encounter
    instances. After successful creation, users are redirected to the
    encounter detail page.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered encounter creation form or redirect to detail
    """
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
    """
    Handle updating existing encounters.

    This view processes encounter update forms and modifies existing
    encounter instances. After successful update, users are redirected
    to the encounter detail page.

    Args:
        request: HTTP request object
        pk: Primary key of the encounter to update

    Returns:
        HttpResponse: Rendered encounter update form or redirect to detail
    """
    encounter = get_object_or_404(Encounter, pk=pk)

    if request.method == "POST":
        form = EncounterForm(request.POST, instance=encounter)
        if form.is_valid():
            form.save()
            return redirect("combat_tracker:encounter_detail", pk=pk)
    else:
        form = EncounterForm(instance=encounter)

    return render(
        request,
        "combat_tracker/encounter_update.html",
        {"form": form, "encounter": encounter},
    )


@login_required
def encounter_delete_view(request, pk):
    """
    Handle deletion of encounters with confirmation.

    This view displays a confirmation page for encounter deletion. Users
    must confirm the deletion by submitting the form. After successful
    deletion, users are redirected to the encounter list page.

    Args:
        request: HTTP request object
        pk: Primary key of the encounter to delete

    Returns:
        HttpResponse: Rendered deletion confirmation page or redirect to list
    """
    encounter = get_object_or_404(Encounter, pk=pk)

    if request.method == "POST":
        encounter.delete()
        return redirect("combat_tracker:encounter_list")

    return render(
        request, "combat_tracker/encounter_delete.html", {"encounter": encounter}
    )


@login_required
def start_encounter_view(request, pk):
    """
    Start a combat session by entering initiative rolls.

    This view handles the transition from encounter planning to active combat.
    It creates a combat session and combat participants based on initiative
    rolls entered by the user. Players manage their own HP while monsters
    get their HP parsed from their stat blocks.

    Args:
        request: HTTP request object
        pk: Primary key of the encounter to start

    Returns:
        HttpResponse: Rendered initiative entry form or redirect to combat interface
    """
    encounter = get_object_or_404(Encounter, pk=pk)

    # Check if combat session already exists
    if hasattr(encounter, "combat_session"):
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
                        participant_type="player",
                        player=player,
                        initiative=initiative,
                        current_hp=0,  # Players manage their own HP
                        max_hp=0,  # Players manage their own HP
                    )

                # Create combat participants for monsters
                for monster in encounter.monsters.all():
                    field_name = f"monster_{monster.id}_initiative"
                    initiative = form.cleaned_data[field_name]
                    monster_hp = parse_monster_hp(monster.hp)
                    CombatParticipant.objects.create(
                        combat_session=combat_session,
                        participant_type="monster",
                        monster=monster,
                        initiative=initiative,
                        current_hp=monster_hp,
                        max_hp=monster_hp,
                    )

                messages.success(
                    request, "Combat started! Initiative order has been set."
                )
                return redirect("combat_tracker:combat_interface", pk=pk)
    else:
        form = InitiativeForm(encounter)

    return render(
        request,
        "combat_tracker/start_encounter.html",
        {"encounter": encounter, "form": form},
    )


@login_required
def combat_interface_view(request, pk):
    """
    Main combat interface showing current turn and participant details.

    This view displays the active combat interface with initiative order,
    current turn information, and participant status. It handles round
    progression and turn management automatically.

    Args:
        request: HTTP request object
        pk: Primary key of the encounter in combat

    Returns:
        HttpResponse: Rendered combat interface page
    """
    encounter = get_object_or_404(Encounter, pk=pk)
    combat_session = get_object_or_404(CombatSession, encounter=encounter)

    # Get all participants for display (including dead ones)
    all_participants = combat_session.participants.all().order_by("-initiative")

    # Get only alive participants for turn sequence
    alive_participants = combat_session.participants.filter(is_dead=False).order_by(
        "-initiative"
    )

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

    current_participant = (
        alive_participants[current_turn_index] if alive_participants.exists() else None
    )

    return render(
        request,
        "combat_tracker/combat_interface.html",
        {
            "encounter": encounter,
            "combat_session": combat_session,
            "all_participants": all_participants,
            "alive_participants": alive_participants,
            "current_participant": current_participant,
            "current_turn_index": current_turn_index,
        },
    )


@login_required
def next_turn_view(request, pk):
    """
    Move to the next turn in combat.

    This view advances the combat to the next turn, marking the current
    turn as completed and moving to the next participant in initiative
    order. When all participants have had their turn, it starts a new round.

    Args:
        request: HTTP request object
        pk: Primary key of the encounter in combat

    Returns:
        HttpResponse: Redirect to combat interface
    """
    encounter = get_object_or_404(Encounter, pk=pk)
    combat_session = get_object_or_404(CombatSession, encounter=encounter)

    # Only work with alive participants
    alive_participants = combat_session.participants.filter(is_dead=False).order_by(
        "-initiative"
    )

    if not alive_participants.exists():
        messages.warning(request, "No active participants in combat!")
        return redirect("combat_tracker:encounter_detail", pk=pk)

    # Mark current turn as completed
    current_turn_index = combat_session.current_turn_index
    if current_turn_index < alive_participants.count():
        current_participant = alive_participants[current_turn_index]
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
    """
    End the current combat session.

    This view handles the termination of an active combat session,
    marking it as inactive and returning users to the encounter detail page.

    Args:
        request: HTTP request object
        pk: Primary key of the encounter in combat

    Returns:
        HttpResponse: Rendered combat end confirmation or redirect to encounter detail
    """
    encounter = get_object_or_404(Encounter, pk=pk)
    combat_session = get_object_or_404(CombatSession, encounter=encounter)

    if request.method == "POST":
        combat_session.is_active = False
        combat_session.save()
        messages.success(request, "Combat has ended!")
        return redirect("combat_tracker:encounter_detail", pk=pk)

    return render(
        request,
        "combat_tracker/end_combat.html",
        {"encounter": encounter, "combat_session": combat_session},
    )


@login_required
def update_hp_view(request, pk, participant_id):
    """
    Update HP for a combat participant (damage/healing).

    This view handles hit point changes during combat, including damage
    and healing. It automatically handles death status when HP reaches 0
    and prevents HP from exceeding maximum values.

    Args:
        request: HTTP request object
        pk: Primary key of the encounter in combat
        participant_id: Primary key of the combat participant

    Returns:
        HttpResponse: Rendered HP update form or redirect to combat interface
    """
    encounter = get_object_or_404(Encounter, pk=pk)
    combat_session = get_object_or_404(CombatSession, encounter=encounter)
    participant = get_object_or_404(
        CombatParticipant, pk=participant_id, combat_session=combat_session
    )

    if request.method == "POST":
        form = HPTrackingForm(request.POST)
        if form.is_valid():
            change_type = form.cleaned_data["change_type"]
            amount = form.cleaned_data["amount"]
            notes = form.cleaned_data.get("notes", "")

            if change_type == "damage":
                participant.current_hp -= amount
                if participant.current_hp <= 0:
                    participant.current_hp = 0
                    participant.is_dead = True
                    messages.success(
                        request,
                        f"{participant.name} takes {amount} damage and is now dead!",
                    )
                else:
                    messages.success(
                        request,
                        f"{participant.name} takes {amount} damage. Current HP: {participant.current_hp}",
                    )
            else:  # healing
                participant.current_hp += amount
                if participant.current_hp > participant.max_hp:
                    participant.current_hp = participant.max_hp
                participant.is_dead = False  # Revive if they were dead
                messages.success(
                    request,
                    f"{participant.name} is healed for {amount} HP. Current HP: {participant.current_hp}",
                )

            participant.save()
            return redirect("combat_tracker:combat_interface", pk=pk)
    else:
        form = HPTrackingForm()

    return render(
        request,
        "combat_tracker/update_hp.html",
        {
            "encounter": encounter,
            "combat_session": combat_session,
            "participant": participant,
            "form": form,
        },
    )
