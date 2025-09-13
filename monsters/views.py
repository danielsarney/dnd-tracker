from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Monster
from .forms import MonsterForm
from campaigns.models import Campaign


class MonsterListView(LoginRequiredMixin, ListView):
    model = Monster
    template_name = 'monsters/monster_list.html'
    context_object_name = 'monsters'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Monster.objects.select_related('campaign').all()
        
        # Filter by campaign if specified
        campaign_id = self.request.GET.get('campaign')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Filter by type if specified
        monster_type = self.request.GET.get('type')
        if monster_type:
            queryset = queryset.filter(monster_type=monster_type)
        
        # Filter by size if specified
        size = self.request.GET.get('size')
        if size:
            queryset = queryset.filter(size=size)
        
        # Filter by challenge rating if specified
        cr_min = self.request.GET.get('cr_min')
        cr_max = self.request.GET.get('cr_max')
        if cr_min:
            queryset = queryset.filter(challenge_rating__gte=float(cr_min))
        if cr_max:
            queryset = queryset.filter(challenge_rating__lte=float(cr_max))
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(monster_type__icontains=search_query) |
                Q(alignment__icontains=search_query) |
                Q(actions__icontains=search_query)
            )
        
        return queryset.order_by('challenge_rating', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        context['monster_types'] = Monster.TYPE_CHOICES
        context['sizes'] = Monster.SIZE_CHOICES
        context['selected_campaign'] = self.request.GET.get('campaign')
        context['selected_type'] = self.request.GET.get('type')
        context['selected_size'] = self.request.GET.get('size')
        context['cr_min'] = self.request.GET.get('cr_min')
        context['cr_max'] = self.request.GET.get('cr_max')
        context['search_query'] = self.request.GET.get('search')
        return context


class MonsterDetailView(LoginRequiredMixin, DetailView):
    model = Monster
    template_name = 'monsters/monster_detail.html'
    context_object_name = 'monster'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.object.campaign
        return context


class MonsterCreateView(LoginRequiredMixin, CreateView):
    model = Monster
    form_class = MonsterForm
    template_name = 'monsters/monster_form.html'
    success_url = reverse_lazy('monsters:monster_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Monster created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        return context


class MonsterUpdateView(LoginRequiredMixin, UpdateView):
    model = Monster
    form_class = MonsterForm
    template_name = 'monsters/monster_form.html'
    
    def get_success_url(self):
        return reverse_lazy('monsters:monster_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Monster updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        return context


class MonsterDeleteView(LoginRequiredMixin, DeleteView):
    model = Monster
    template_name = 'monsters/monster_confirm_delete.html'
    success_url = reverse_lazy('monsters:monster_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Monster deleted successfully!')
        return super().form_valid(form)


class CampaignMonstersView(LoginRequiredMixin, ListView):
    model = Monster
    template_name = 'monsters/campaign_monsters.html'
    context_object_name = 'monsters'
    paginate_by = 12
    
    def get_queryset(self):
        self.campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_pk'])
        return Monster.objects.filter(campaign=self.campaign).order_by('challenge_rating', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        return context