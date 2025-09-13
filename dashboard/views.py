from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from campaigns.models import Campaign
from players.models import Player
from npcs.models import NPC
from monsters.models import Monster
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
    total_players = Player.objects.count()
    total_npcs = NPC.objects.count()
    total_monsters = Monster.objects.count()
    total_sessions = GameSession.objects.count()
    
    # Get user-specific counts
    user_campaign_count = user_campaigns.count()
    user_player_count = Player.objects.filter(
        campaign__dm__iexact=user.username
    ).count()
    user_npc_count = NPC.objects.filter(
        campaign__dm__iexact=user.username
    ).count()
    user_monster_count = Monster.objects.filter(
        campaign__dm__iexact=user.username
    ).count()
    user_session_count = GameSession.objects.filter(
        campaign__dm__iexact=user.username
    ).count()
    
    # Get recent players
    recent_players = Player.objects.filter(
        campaign__dm__iexact=user.username
    ).order_by('-created_at')[:3]
    
    # Get recent NPCs
    recent_npcs = NPC.objects.filter(
        campaign__dm__iexact=user.username
    ).order_by('-created_at')[:3]
    
    # Get recent monsters
    recent_monsters = Monster.objects.filter(
        campaign__dm__iexact=user.username
    ).order_by('-created_at')[:3]
    
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
    
    
    # Get campaign activity (sessions in last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_activity = GameSession.objects.filter(
        campaign__dm__iexact=user.username,
        date__gte=thirty_days_ago
    ).count()
    
    context = {
        'user_campaigns': user_campaigns,
        'recent_players': recent_players,
        'recent_npcs': recent_npcs,
        'recent_monsters': recent_monsters,
        'recent_sessions': recent_sessions,
        'upcoming_sessions': upcoming_sessions,
        'today_sessions': today_sessions,
        'total_campaigns': total_campaigns,
        'total_players': total_players,
        'total_npcs': total_npcs,
        'total_monsters': total_monsters,
        'total_sessions': total_sessions,
        'user_campaign_count': user_campaign_count,
        'user_player_count': user_player_count,
        'user_npc_count': user_npc_count,
        'user_monster_count': user_monster_count,
        'user_session_count': user_session_count,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
