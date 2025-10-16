"""
Monster Views for D&D Tracker

This module contains all the view functions for monster management.
It handles CRUD operations for monsters including listing, creating,
updating, and deleting monsters with search functionality.

Key Features:
- Monster listing with search functionality
- Monster creation and editing
- Monster detail viewing
- Monster deletion with confirmation
- Search across name, challenge rating, traits, and actions
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Monster
from .forms import MonsterForm


@login_required
def monster_list_view(request):
    """
    Display a list of all monsters with optional search functionality.

    This view shows all monsters in the system and allows users to search
    through monster names, challenge ratings, traits, and actions using
    a search query parameter.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered monster list page with search results
    """
    monsters = Monster.objects.all()

    # Handle search functionality across multiple monster fields
    search_query = request.GET.get("search")
    if search_query:
        monsters = monsters.filter(
            models.Q(name__icontains=search_query)
            | models.Q(challenge_rating__icontains=search_query)
            | models.Q(traits__icontains=search_query)
            | models.Q(actions__icontains=search_query)
        )

    return render(
        request,
        "monsters/monster_list.html",
        {"monsters": monsters, "search_query": search_query},
    )


@login_required
def monster_detail_view(request, pk):
    """
    Display detailed information about a specific monster.

    This view shows all the details of a monster including its name,
    armor class, hit points, ability scores, combat features, and
    special abilities.

    Args:
        request: HTTP request object
        pk: Primary key of the monster to display

    Returns:
        HttpResponse: Rendered monster detail page
    """
    monster = get_object_or_404(Monster, pk=pk)
    return render(request, "monsters/monster_detail.html", {"monster": monster})


@login_required
def monster_create_view(request):
    """
    Handle creation of new monsters.

    This view processes monster creation forms and creates new monster
    instances. After successful creation, users are redirected to the
    monster list page.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered monster creation form or redirect to list
    """
    if request.method == "POST":
        form = MonsterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("monsters:monster_list")
    else:
        form = MonsterForm()

    return render(request, "monsters/monster_create.html", {"form": form})


@login_required
def monster_update_view(request, pk):
    """
    Handle updating existing monsters.

    This view processes monster update forms and modifies existing
    monster instances. After successful update, users are redirected
    to the monster detail page.

    Args:
        request: HTTP request object
        pk: Primary key of the monster to update

    Returns:
        HttpResponse: Rendered monster update form or redirect to detail
    """
    monster = get_object_or_404(Monster, pk=pk)

    if request.method == "POST":
        form = MonsterForm(request.POST, instance=monster)
        if form.is_valid():
            form.save()
            return redirect("monsters:monster_detail", pk=pk)
    else:
        form = MonsterForm(instance=monster)

    return render(
        request, "monsters/monster_update.html", {"form": form, "monster": monster}
    )


@login_required
def monster_delete_view(request, pk):
    """
    Handle deletion of monsters with confirmation.

    This view displays a confirmation page for monster deletion. Users
    must confirm the deletion by submitting the form. After successful
    deletion, users are redirected to the monster list page.

    Args:
        request: HTTP request object
        pk: Primary key of the monster to delete

    Returns:
        HttpResponse: Rendered deletion confirmation page or redirect to list
    """
    monster = get_object_or_404(Monster, pk=pk)

    if request.method == "POST":
        monster.delete()
        return redirect("monsters:monster_list")

    return render(request, "monsters/monster_delete.html", {"monster": monster})
