from django.db import models
from campaigns.models import Campaign


class Character(models.Model):
    CHARACTER_TYPES = [
        ('PLAYER', 'Player'),
        ('NPC', 'NPC'),
        ('MONSTER', 'Monster'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='characters')
    type = models.CharField(max_length=7, choices=CHARACTER_TYPES, default='PLAYER')
    name = models.CharField(max_length=120)
    race = models.CharField(max_length=80, blank=True, null=True)
    character_class = models.CharField(max_length=80, blank=True, null=True)
    background = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True, help_text="D&D Beyond or other reference URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['type', 'name']
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('characters:character_detail', kwargs={'pk': self.pk})
    
    @property
    def is_player(self):
        return self.type == 'PLAYER'
    
    @property
    def is_npc(self):
        return self.type == 'NPC'
    
    @property
    def is_monster(self):
        return self.type == 'MONSTER'
