from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Encounter
from .forms import EncounterForm


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
