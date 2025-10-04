from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Session
from .forms import SessionForm


@login_required
def session_list_view(request):
    """Display list of sessions with search functionality"""
    sessions = Session.objects.all()

    # Handle search functionality
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
    """Display session details"""
    session = get_object_or_404(Session, pk=pk)
    return render(request, "game_sessions/session_detail.html", {"session": session})


@login_required
def session_create_view(request):
    """Create a new session"""
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
    """Update an existing session"""
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
    """Delete a session"""
    session = get_object_or_404(Session, pk=pk)

    if request.method == "POST":
        session.delete()
        return redirect("game_sessions:session_list")

    return render(request, "game_sessions/session_delete.html", {"session": session})
