from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Player
from .forms import PlayerForm


@login_required
def player_list_view(request):
    """Display list of players with search functionality"""
    players = Player.objects.all()

    # Handle search functionality
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
    """Display player details"""
    player = get_object_or_404(Player, pk=pk)
    return render(request, "players/player_detail.html", {"player": player})


@login_required
def player_create_view(request):
    """Create a new player"""
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
    """Update an existing player"""
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
    """Delete a player"""
    player = get_object_or_404(Player, pk=pk)

    if request.method == "POST":
        player.delete()
        return redirect("players:player_list")

    return render(request, "players/player_delete.html", {"player": player})
