from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import GameSession
from .forms import GameSessionForm
from campaigns.models import Campaign


class GameSessionListView(LoginRequiredMixin, ListView):
    model = GameSession
    template_name = 'game_sessions/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = GameSession.objects.select_related('campaign').all()
        
        # Filter by campaign if specified
        campaign_id = self.request.GET.get('campaign')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Filter by session date if specified
        session_date = self.request.GET.get('session_date')
        if session_date:
            queryset = queryset.filter(date=session_date)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(summary__icontains=search_query) |
                Q(campaign__name__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        context['selected_campaign'] = self.request.GET.get('campaign')
        context['selected_session_date'] = self.request.GET.get('session_date')
        context['session_dates'] = GameSession.objects.values_list('date', flat=True).distinct().order_by('-date')
        context['search_query'] = self.request.GET.get('search')
        return context


class GameSessionDetailView(LoginRequiredMixin, DetailView):
    model = GameSession
    template_name = 'game_sessions/session_detail.html'
    context_object_name = 'session'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.object.campaign
        return context


class GameSessionCreateView(LoginRequiredMixin, CreateView):
    model = GameSession
    form_class = GameSessionForm
    template_name = 'game_sessions/session_form.html'
    success_url = reverse_lazy('game_sessions:session_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Game session created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        return context


class GameSessionUpdateView(LoginRequiredMixin, UpdateView):
    model = GameSession
    form_class = GameSessionForm
    template_name = 'game_sessions/session_form.html'
    
    def get_success_url(self):
        return reverse_lazy('game_sessions:session_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Game session updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        return context


class GameSessionDeleteView(LoginRequiredMixin, DeleteView):
    model = GameSession
    template_name = 'game_sessions/session_confirm_delete.html'
    success_url = reverse_lazy('game_sessions:session_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Game session deleted successfully!')
        return super().form_valid(form)


class CampaignSessionsView(LoginRequiredMixin, ListView):
    model = GameSession
    template_name = 'game_sessions/campaign_sessions.html'
    context_object_name = 'sessions'
    paginate_by = 12
    
    def get_queryset(self):
        self.campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_pk'])
        return GameSession.objects.filter(campaign=self.campaign)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        return context
