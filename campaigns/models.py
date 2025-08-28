from django.db import models


class Campaign(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    dm = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('campaigns:campaign_detail', kwargs={'pk': self.pk})
