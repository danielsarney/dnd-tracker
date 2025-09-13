from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Player
from .forms import PlayerForm
from campaigns.models import Campaign


class PlayerListView(LoginRequiredMixin, ListView):
    model = Player
    template_name = 'players/player_list.html'
    context_object_name = 'players'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Player.objects.select_related('campaign').all()
        
        # Filter by campaign if specified
        campaign_id = self.request.GET.get('campaign')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(race__icontains=search_query) |
                Q(character_class__icontains=search_query) |
                Q(background__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        context['selected_campaign'] = self.request.GET.get('campaign')
        context['search_query'] = self.request.GET.get('search')
        return context


class PlayerDetailView(LoginRequiredMixin, DetailView):
    model = Player
    template_name = 'players/player_detail.html'
    context_object_name = 'player'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.object.campaign
        return context


class PlayerCreateView(LoginRequiredMixin, CreateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/player_form.html'
    success_url = reverse_lazy('players:player_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Player created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        return context


class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/player_form.html'
    
    def get_success_url(self):
        return reverse_lazy('players:player_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Player updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        return context


class PlayerDeleteView(LoginRequiredMixin, DeleteView):
    model = Player
    template_name = 'players/player_confirm_delete.html'
    success_url = reverse_lazy('players:player_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Player deleted successfully!')
        return super().form_valid(form)


class CampaignPlayersView(LoginRequiredMixin, ListView):
    model = Player
    template_name = 'players/campaign_players.html'
    context_object_name = 'players'
    paginate_by = 12
    
    def get_queryset(self):
        self.campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_pk'])
        return Player.objects.filter(campaign=self.campaign)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        return context