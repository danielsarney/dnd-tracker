from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Campaign
from .forms import CampaignForm


@login_required
def campaign_list_view(request):
    """Display list of campaigns with search functionality"""
    campaigns = Campaign.objects.all()

    # Handle search functionality
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
    """Display campaign details"""
    campaign = get_object_or_404(Campaign, pk=pk)
    return render(request, "campaigns/campaign_detail.html", {"campaign": campaign})


@login_required
def campaign_create_view(request):
    """Create a new campaign"""
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
    """Update an existing campaign"""
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
    """Delete a campaign"""
    campaign = get_object_or_404(Campaign, pk=pk)

    if request.method == "POST":
        campaign.delete()
        return redirect("campaigns:campaign_list")

    return render(request, "campaigns/campaign_delete.html", {"campaign": campaign})
