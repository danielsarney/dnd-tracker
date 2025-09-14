from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Monster
from .forms import MonsterForm


class MonsterListView(LoginRequiredMixin, ListView):
    model = Monster
    template_name = 'monsters/monster_list.html'
    context_object_name = 'monsters'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Monster.objects.all()
        
        # Filter by type if specified
        monster_type = self.request.GET.get('type')
        if monster_type:
            queryset = queryset.filter(monster_type=monster_type)
        
        # Filter by size if specified
        size = self.request.GET.get('size')
        if size:
            queryset = queryset.filter(size=size)
        
        # Filter by challenge rating if specified
        challenge_rating = self.request.GET.get('challenge_rating')
        if challenge_rating:
            queryset = queryset.filter(challenge_rating=float(challenge_rating))
        
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
        context['monster_types'] = Monster.TYPE_CHOICES
        context['sizes'] = Monster.SIZE_CHOICES
        context['challenge_ratings'] = [
            0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30
        ]
        context['selected_type'] = self.request.GET.get('type')
        context['selected_size'] = self.request.GET.get('size')
        context['selected_cr'] = self.request.GET.get('challenge_rating')
        context['search_query'] = self.request.GET.get('search')
        return context


class MonsterDetailView(LoginRequiredMixin, DetailView):
    model = Monster
    template_name = 'monsters/monster_detail.html'
    context_object_name = 'monster'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MonsterCreateView(LoginRequiredMixin, CreateView):
    model = Monster
    form_class = MonsterForm
    template_name = 'monsters/monster_form.html'
    success_url = reverse_lazy('monsters:monster_list')
    
    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Monster created successfully!')
        return redirect('monsters:monster_detail', pk=self.object.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MonsterUpdateView(LoginRequiredMixin, UpdateView):
    model = Monster
    form_class = MonsterForm
    template_name = 'monsters/monster_form.html'
    
    def get_success_url(self):
        return reverse_lazy('monsters:monster_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Monster updated successfully!')
        return redirect('monsters:monster_detail', pk=self.object.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MonsterDeleteView(LoginRequiredMixin, DeleteView):
    model = Monster
    template_name = 'monsters/monster_confirm_delete.html'
    success_url = reverse_lazy('monsters:monster_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Monster deleted successfully!')
        return super().form_valid(form)

