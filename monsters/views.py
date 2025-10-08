from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Monster
from .forms import MonsterForm


@login_required
def monster_list_view(request):
    """Display list of monsters with search functionality"""
    monsters = Monster.objects.all()

    # Handle search functionality
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
    """Display monster details"""
    monster = get_object_or_404(Monster, pk=pk)
    return render(request, "monsters/monster_detail.html", {"monster": monster})


@login_required
def monster_create_view(request):
    """Create a new monster"""
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
    """Update an existing monster"""
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
    """Delete a monster"""
    monster = get_object_or_404(Monster, pk=pk)

    if request.method == "POST":
        monster.delete()
        return redirect("monsters:monster_list")

    return render(request, "monsters/monster_delete.html", {"monster": monster})
