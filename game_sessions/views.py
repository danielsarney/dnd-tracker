"""
Game Session Views for D&D Tracker

This module contains all the view functions for game session management.
It handles CRUD operations for game sessions including listing, creating,
updating, and deleting sessions with search functionality.

Key Features:
- Game session listing with search functionality
- Session creation and editing
- Session detail viewing
- Session deletion with confirmation
- Search across campaign title, planning notes, and session notes
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Session
from .forms import SessionForm


@login_required
def session_list_view(request):
    """
    Display a list of all game sessions with optional search functionality.

    This view shows all game sessions in the system and allows users to search
    through campaign titles, planning notes, and session notes using a search
    query parameter.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered session list page with search results
    """
    sessions = Session.objects.all()

    # Handle search functionality across multiple session fields
    search_query = request.GET.get("search")
    if search_query:
        sessions = sessions.filter(
            models.Q(campaign__title__icontains=search_query)
            | models.Q(planning_notes__icontains=search_query)
            | models.Q(session_notes__icontains=search_query)
        )

    return render(
        request,
        "game_sessions/session_list.html",
        {"sessions": sessions, "search_query": search_query},
    )


@login_required
def session_detail_view(request, pk):
    """
    Display detailed information about a specific game session.

    This view shows all the details of a game session including its
    associated campaign, planning notes, session notes, and session date.

    Args:
        request: HTTP request object
        pk: Primary key of the session to display

    Returns:
        HttpResponse: Rendered session detail page
    """
    session = get_object_or_404(Session, pk=pk)
    return render(request, "game_sessions/session_detail.html", {"session": session})


@login_required
def session_create_view(request):
    """
    Handle creation of new game sessions.

    This view processes game session creation forms and creates new
    session instances. After successful creation, users are redirected
    to the session list page.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered session creation form or redirect to list
    """
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("game_sessions:session_list")
    else:
        form = SessionForm()

    return render(request, "game_sessions/session_create.html", {"form": form})


@login_required
def session_update_view(request, pk):
    """
    Handle updating existing game sessions.

    This view processes game session update forms and modifies existing
    session instances. After successful update, users are redirected
    to the session detail page.

    Args:
        request: HTTP request object
        pk: Primary key of the session to update

    Returns:
        HttpResponse: Rendered session update form or redirect to detail
    """
    session = get_object_or_404(Session, pk=pk)

    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            return redirect("game_sessions:session_detail", pk=pk)
    else:
        form = SessionForm(instance=session)

    return render(
        request, "game_sessions/session_update.html", {"form": form, "session": session}
    )


@login_required
def session_delete_view(request, pk):
    """
    Handle deletion of game sessions with confirmation.

    This view displays a confirmation page for game session deletion.
    Users must confirm the deletion by submitting the form. After successful
    deletion, users are redirected to the session list page.

    Args:
        request: HTTP request object
        pk: Primary key of the session to delete

    Returns:
        HttpResponse: Rendered deletion confirmation page or redirect to list
    """
    session = get_object_or_404(Session, pk=pk)

    if request.method == "POST":
        session.delete()
        return redirect("game_sessions:session_list")

    return render(request, "game_sessions/session_delete.html", {"session": session})
