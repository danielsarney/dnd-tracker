from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Character
from .forms import CharacterForm
from campaigns.models import Campaign


class CharacterListView(LoginRequiredMixin, ListView):
    model = Character
    template_name = 'characters/character_list.html'
    context_object_name = 'characters'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Character.objects.select_related('campaign').all()
        
        # Filter by campaign if specified
        campaign_id = self.request.GET.get('campaign')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Filter by type if specified
        character_type = self.request.GET.get('type')
        if character_type:
            queryset = queryset.filter(type=character_type)
        
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
        context['character_types'] = Character.CHARACTER_TYPES
        context['selected_campaign'] = self.request.GET.get('campaign')
        context['selected_type'] = self.request.GET.get('type')
        context['search_query'] = self.request.GET.get('search')
        return context


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = 'characters/character_detail.html'
    context_object_name = 'character'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.object.campaign
        return context


class CharacterCreateView(LoginRequiredMixin, CreateView):
    model = Character
    form_class = CharacterForm
    template_name = 'characters/character_form.html'
    success_url = reverse_lazy('characters:character_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Character created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        return context


class CharacterUpdateView(LoginRequiredMixin, UpdateView):
    model = Character
    form_class = CharacterForm
    template_name = 'characters/character_form.html'
    
    def get_success_url(self):
        return reverse_lazy('characters:character_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Character updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        return context


class CharacterDeleteView(LoginRequiredMixin, DeleteView):
    model = Character
    template_name = 'characters/character_confirm_delete.html'
    success_url = reverse_lazy('characters:character_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Character deleted successfully!')
        return super().form_valid(form)


class CampaignCharactersView(LoginRequiredMixin, ListView):
    model = Character
    template_name = 'characters/campaign_characters.html'
    context_object_name = 'characters'
    paginate_by = 12
    
    def get_queryset(self):
        self.campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_pk'])
        return Character.objects.filter(campaign=self.campaign)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        return context
