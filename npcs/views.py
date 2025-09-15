from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import NPC
from .forms import NPCForm
from campaigns.models import Campaign


class NPCListView(LoginRequiredMixin, ListView):
    model = NPC
    template_name = 'npcs/npc_list.html'
    context_object_name = 'npcs'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = NPC.objects.all()
        
        # Filter by race if specified
        race = self.request.GET.get('race')
        if race:
            queryset = queryset.filter(race__icontains=race)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(race__icontains=search_query) |
                Q(occupation__icontains=search_query) |
                Q(background__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search')
        return context


class NPCDetailView(LoginRequiredMixin, DetailView):
    model = NPC
    template_name = 'npcs/npc_detail.html'
    context_object_name = 'npc'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NPCCreateView(LoginRequiredMixin, CreateView):
    model = NPC
    form_class = NPCForm
    template_name = 'npcs/npc_form.html'
    success_url = reverse_lazy('npcs:npc_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'NPC created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NPCUpdateView(LoginRequiredMixin, UpdateView):
    model = NPC
    form_class = NPCForm
    template_name = 'npcs/npc_form.html'
    
    def get_success_url(self):
        return reverse_lazy('npcs:npc_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'NPC updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NPCDeleteView(LoginRequiredMixin, DeleteView):
    model = NPC
    template_name = 'npcs/npc_confirm_delete.html'
    success_url = reverse_lazy('npcs:npc_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'NPC deleted successfully!')
        return super().form_valid(form)


class CampaignNPCsView(LoginRequiredMixin, ListView):
    model = NPC
    template_name = 'npcs/campaign_npcs.html'
    context_object_name = 'npcs'
    paginate_by = 12
    
    def get_queryset(self):
        self.campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_pk'])
        # Since NPCs no longer have a campaign field, return all NPCs
        # You may want to implement a different filtering mechanism
        return NPC.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        return context