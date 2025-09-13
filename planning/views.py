from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import PlanningSession
from .forms import PlanningSessionForm
from campaigns.models import Campaign


class PlanningSessionListView(LoginRequiredMixin, ListView):
    model = PlanningSession
    template_name = 'planning/planning_list.html'
    context_object_name = 'planning_sessions'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = PlanningSession.objects.select_related('campaign').all()
        
        # Filter by campaign if specified
        campaign_id = self.request.GET.get('campaign')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(notes__icontains=search_query) |
                Q(campaign__name__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        context['selected_campaign'] = self.request.GET.get('campaign')
        context['search_query'] = self.request.GET.get('search')
        return context


class PlanningSessionDetailView(LoginRequiredMixin, DetailView):
    model = PlanningSession
    template_name = 'planning/planning_detail.html'
    context_object_name = 'planning_session'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.object.campaign
        return context


class PlanningSessionCreateView(LoginRequiredMixin, CreateView):
    model = PlanningSession
    form_class = PlanningSessionForm
    template_name = 'planning/planning_form.html'
    success_url = reverse_lazy('planning:planning_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Planning session created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        return context


class PlanningSessionUpdateView(LoginRequiredMixin, UpdateView):
    model = PlanningSession
    form_class = PlanningSessionForm
    template_name = 'planning/planning_form.html'
    
    def get_success_url(self):
        return reverse_lazy('planning:planning_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Planning session updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaigns'] = Campaign.objects.all()
        return context


class PlanningSessionDeleteView(LoginRequiredMixin, DeleteView):
    model = PlanningSession
    template_name = 'planning/planning_confirm_delete.html'
    success_url = reverse_lazy('planning:planning_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Planning session deleted successfully!')
        return super().form_valid(form)


class CampaignPlanningView(LoginRequiredMixin, ListView):
    model = PlanningSession
    template_name = 'planning/campaign_planning.html'
    context_object_name = 'planning_sessions'
    paginate_by = 12
    
    def get_queryset(self):
        self.campaign = get_object_or_404(Campaign, pk=self.kwargs['campaign_pk'])
        return PlanningSession.objects.filter(campaign=self.campaign)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        return context
