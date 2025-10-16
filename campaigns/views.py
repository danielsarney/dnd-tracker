"""
Campaign Views for D&D Tracker

This module contains all the view functions for campaign management.
It handles CRUD operations for campaigns including listing, creating,
updating, and deleting campaigns with search functionality.

Key Features:
- Campaign listing with search functionality
- Campaign creation and editing
- Campaign detail viewing
- Campaign deletion with confirmation
- Search across title, description, introduction, and requirements
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Campaign
from .forms import CampaignForm


@login_required
def campaign_list_view(request):
    """
    Display a list of all campaigns with optional search functionality.

    This view shows all campaigns in the system and allows users to search
    through campaign titles, descriptions, introductions, and character
    requirements using a search query parameter.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered campaign list page with search results
    """
    campaigns = Campaign.objects.all()

    # Handle search functionality across multiple fields
    search_query = request.GET.get("search")
    if search_query:
        campaigns = campaigns.filter(
            models.Q(title__icontains=search_query)
            | models.Q(description__icontains=search_query)
            | models.Q(introduction__icontains=search_query)
            | models.Q(character_requirements__icontains=search_query)
        )

    return render(
        request,
        "campaigns/campaign_list.html",
        {"campaigns": campaigns, "search_query": search_query},
    )


@login_required
def campaign_detail_view(request, pk):
    """
    Display detailed information about a specific campaign.

    This view shows all the details of a campaign including its title,
    description, introduction, and character requirements.

    Args:
        request: HTTP request object
        pk: Primary key of the campaign to display

    Returns:
        HttpResponse: Rendered campaign detail page
    """
    campaign = get_object_or_404(Campaign, pk=pk)
    return render(request, "campaigns/campaign_detail.html", {"campaign": campaign})


@login_required
def campaign_create_view(request):
    """
    Handle creation of new campaigns.

    This view processes campaign creation forms and creates new campaign
    instances. After successful creation, users are redirected to the
    campaign list page.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered campaign creation form or redirect to list
    """
    if request.method == "POST":
        form = CampaignForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("campaigns:campaign_list")
    else:
        form = CampaignForm()

    return render(request, "campaigns/campaign_create.html", {"form": form})


@login_required
def campaign_update_view(request, pk):
    """
    Handle updating existing campaigns.

    This view processes campaign update forms and modifies existing campaign
    instances. After successful update, users are redirected to the campaign
    detail page.

    Args:
        request: HTTP request object
        pk: Primary key of the campaign to update

    Returns:
        HttpResponse: Rendered campaign update form or redirect to detail
    """
    campaign = get_object_or_404(Campaign, pk=pk)

    if request.method == "POST":
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            return redirect("campaigns:campaign_detail", pk=pk)
    else:
        form = CampaignForm(instance=campaign)

    return render(
        request, "campaigns/campaign_update.html", {"form": form, "campaign": campaign}
    )


@login_required
def campaign_delete_view(request, pk):
    """
    Handle deletion of campaigns with confirmation.

    This view displays a confirmation page for campaign deletion. Users
    must confirm the deletion by submitting the form. After successful
    deletion, users are redirected to the campaign list page.

    Args:
        request: HTTP request object
        pk: Primary key of the campaign to delete

    Returns:
        HttpResponse: Rendered deletion confirmation page or redirect to list
    """
    campaign = get_object_or_404(Campaign, pk=pk)

    if request.method == "POST":
        campaign.delete()
        return redirect("campaigns:campaign_list")

    return render(request, "campaigns/campaign_delete.html", {"campaign": campaign})
