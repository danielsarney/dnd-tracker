from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Campaign
from .forms import CampaignForm


class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = 'campaigns/campaign_list.html'
    context_object_name = 'campaigns'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Campaign.objects.all()
        
        # Filter by DM
        dm = self.request.GET.get('dm')
        if dm:
            queryset = queryset.filter(dm=dm)
        
        # Search by name or description
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get unique DMs for filter dropdown
        context['dms'] = Campaign.objects.values_list('dm', flat=True).distinct().order_by('dm')
        
        # Pass current filter values
        context['selected_dm'] = self.request.GET.get('dm', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        return context


class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = 'campaigns/campaign_detail.html'
    context_object_name = 'campaign'


class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/campaign_form.html'
    success_url = reverse_lazy('campaigns:campaign_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Campaign created successfully!')
        return super().form_valid(form)


class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/campaign_form.html'
    
    def get_success_url(self):
        return reverse_lazy('campaigns:campaign_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Campaign updated successfully!')
        return super().form_valid(form)


class CampaignDeleteView(LoginRequiredMixin, DeleteView):
    model = Campaign
    template_name = 'campaigns/campaign_confirm_delete.html'
    success_url = reverse_lazy('campaigns:campaign_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Campaign deleted successfully!')
        return super().form_valid(form)
