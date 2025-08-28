from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from campaigns.models import Campaign
from characters.models import Character
from game_sessions.models import GameSession
from django.utils import timezone
from datetime import timedelta


@login_required
def dashboard(request):
    """Main dashboard view showing user's D&D tracker overview"""
    user = request.user
    
    # Get user's campaigns (user is DM)
    user_campaigns = Campaign.objects.filter(
        dm__iexact=user.username
    ).order_by('-created_at')[:5]
    
    # Get total counts
    total_campaigns = Campaign.objects.count()
    total_characters = Character.objects.count()
    total_sessions = GameSession.objects.count()
    
    # Get user-specific counts
    user_campaign_count = user_campaigns.count()
    user_character_count = Character.objects.filter(
        campaign__dm__iexact=user.username
    ).count()
    user_session_count = GameSession.objects.filter(
        campaign__dm__iexact=user.username
    ).count()
    
    # Get recent characters
    recent_characters = Character.objects.filter(
        campaign__dm__iexact=user.username
    ).order_by('-created_at')[:6]
    
    # Get recent game sessions
    recent_sessions = GameSession.objects.filter(
        campaign__dm__iexact=user.username
    ).order_by('-date')[:5]
    
    # Get upcoming sessions (next 7 days)
    upcoming_sessions = GameSession.objects.filter(
        campaign__dm__iexact=user.username,
        date__gte=timezone.now().date(),
        date__lte=timezone.now().date() + timedelta(days=7)
    ).order_by('date')[:5]
    
    # Get today's sessions
    today_sessions = GameSession.objects.filter(
        campaign__dm__iexact=user.username,
        date=timezone.now().date()
    )
    
    # Get character type distribution
    player_characters = Character.objects.filter(
        campaign__dm__iexact=user.username,
        type='PLAYER'
    ).count()
    
    npc_characters = Character.objects.filter(
        campaign__dm__iexact=user.username,
        type='NPC'
    ).count()
    
    # Get campaign activity (sessions in last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_activity = GameSession.objects.filter(
        campaign__dm__iexact=user.username,
        date__gte=thirty_days_ago
    ).count()
    
    context = {
        'user_campaigns': user_campaigns,
        'recent_characters': recent_characters,
        'recent_sessions': recent_sessions,
        'upcoming_sessions': upcoming_sessions,
        'today_sessions': today_sessions,
        'total_campaigns': total_campaigns,
        'total_characters': total_characters,
        'total_sessions': total_sessions,
        'user_campaign_count': user_campaign_count,
        'user_character_count': user_character_count,
        'user_session_count': user_session_count,
        'player_characters': player_characters,
        'npc_characters': npc_characters,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
