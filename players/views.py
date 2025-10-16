"""
Player Character Views for D&D Tracker

This module contains all the view functions for player character management.
It handles CRUD operations for player characters including listing, creating,
updating, and deleting characters with search functionality.

Key Features:
- Player character listing with search functionality
- Character creation and editing
- Character detail viewing
- Character deletion with confirmation
- Search across character name, player name, class, subclass, race, background, and campaign
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Player
from .forms import PlayerForm


@login_required
def player_list_view(request):
    """
    Display a list of all player characters with optional search functionality.

    This view shows all player characters in the system and allows users to search
    through character names, player names, classes, subclasses, races, backgrounds,
    and associated campaigns using a search query parameter.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered player list page with search results
    """
    players = Player.objects.all()

    # Handle search functionality across multiple character fields
    search_query = request.GET.get("search")
    if search_query:
        players = players.filter(
            models.Q(character_name__icontains=search_query)
            | models.Q(player_name__icontains=search_query)
            | models.Q(character_class__icontains=search_query)
            | models.Q(subclass__icontains=search_query)
            | models.Q(race__icontains=search_query)
            | models.Q(background__icontains=search_query)
            | models.Q(campaign__title__icontains=search_query)
        )

    return render(
        request,
        "players/player_list.html",
        {"players": players, "search_query": search_query},
    )


@login_required
def player_detail_view(request, pk):
    """
    Display detailed information about a specific player character.

    This view shows all the details of a player character including their
    name, class, race, level, armor class, background, and associated campaign.

    Args:
        request: HTTP request object
        pk: Primary key of the player character to display

    Returns:
        HttpResponse: Rendered player detail page
    """
    player = get_object_or_404(Player, pk=pk)
    return render(request, "players/player_detail.html", {"player": player})


@login_required
def player_create_view(request):
    """
    Handle creation of new player characters.

    This view processes player character creation forms and creates new
    character instances. After successful creation, users are redirected
    to the player list page.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered player creation form or redirect to list
    """
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("players:player_list")
    else:
        form = PlayerForm()

    return render(request, "players/player_create.html", {"form": form})


@login_required
def player_update_view(request, pk):
    """
    Handle updating existing player characters.

    This view processes player character update forms and modifies existing
    character instances. After successful update, users are redirected to
    the character detail page.

    Args:
        request: HTTP request object
        pk: Primary key of the player character to update

    Returns:
        HttpResponse: Rendered player update form or redirect to detail
    """
    player = get_object_or_404(Player, pk=pk)

    if request.method == "POST":
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect("players:player_detail", pk=pk)
    else:
        form = PlayerForm(instance=player)

    return render(
        request, "players/player_update.html", {"form": form, "player": player}
    )


@login_required
def player_delete_view(request, pk):
    """
    Handle deletion of player characters with confirmation.

    This view displays a confirmation page for player character deletion.
    Users must confirm the deletion by submitting the form. After successful
    deletion, users are redirected to the player list page.

    Args:
        request: HTTP request object
        pk: Primary key of the player character to delete

    Returns:
        HttpResponse: Rendered deletion confirmation page or redirect to list
    """
    player = get_object_or_404(Player, pk=pk)

    if request.method == "POST":
        player.delete()
        return redirect("players:player_list")

    return render(request, "players/player_delete.html", {"player": player})
