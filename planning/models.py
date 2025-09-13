from django.db import models
from campaigns.models import Campaign
from datetime import date


class PlanningSession(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='planning_sessions')
    session_date = models.DateField(help_text="The date this planning session is for")
    title = models.CharField(max_length=200, help_text="Brief title for this planning session")
    notes = models.TextField(help_text="Your preparation notes for this session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-session_date', '-created_at']
        verbose_name = 'Planning Session'
        verbose_name_plural = 'Planning Sessions'
        unique_together = ['campaign', 'session_date']  # One planning session per campaign per date
    
    def __str__(self):
        return f"{self.campaign.name} - {self.session_date.strftime('%B %d, %Y')} - {self.title}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('planning:planning_detail', kwargs={'pk': self.pk})
    
    @property
    def is_today(self):
        from django.utils import timezone
        return self.session_date == timezone.now().date()
    
    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.session_date >= timezone.now().date()
    
    @property
    def is_past(self):
        from django.utils import timezone
        return self.session_date < timezone.now().date()
