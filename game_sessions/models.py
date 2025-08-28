from django.db import models
from campaigns.models import Campaign
from datetime import date


class GameSession(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField(default=date.today)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Game Session'
        verbose_name_plural = 'Game Sessions'
    
    def __str__(self):
        return f"{self.campaign.name} - {self.date.strftime('%B %d, %Y')}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('game_sessions:session_detail', kwargs={'pk': self.pk})
    
    @property
    def is_today(self):
        from django.utils import timezone
        return self.date == timezone.now().date()
    
    @property
    def is_recent(self):
        from django.utils import timezone
        from datetime import timedelta
        return self.date >= timezone.now().date() - timedelta(days=7)
