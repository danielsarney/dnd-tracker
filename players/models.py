from django.db import models
from campaigns.models import Campaign


class Player(models.Model):
    """Represents a player character in a campaign"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='players')
    character_name = models.CharField(max_length=120, help_text="Character's name", default="Unknown Character")
    player_name = models.CharField(max_length=120, help_text="Real-life player's name", default="Unknown Player")
    background = models.TextField(help_text="Character background for story integration", default="No background provided")
    level = models.PositiveIntegerField(default=1, help_text="Character level")
    armor_class = models.PositiveIntegerField(default=10, help_text="Armor Class for combat tracking")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['character_name']
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
    
    def __str__(self):
        return f"{self.character_name} (played by {self.player_name})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('players:player_detail', kwargs={'pk': self.pk})