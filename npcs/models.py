from django.db import models
from campaigns.models import Campaign


class NPC(models.Model):
    """Represents a Non-Player Character in a campaign"""
    NPC_TYPES = [
        ('ALLY', 'Ally'),
        ('NEUTRAL', 'Neutral'),
        ('ENEMY', 'Enemy'),
        ('MERCHANT', 'Merchant'),
        ('QUESTGIVER', 'Quest Giver'),
        ('INFORMATION', 'Information Source'),
    ]
    
    DISPOSITION_CHOICES = [
        ('Friendly', 'Friendly'),
        ('Neutral', 'Neutral'),
        ('Suspicious', 'Suspicious'),
        ('Hostile', 'Hostile'),
        ('Helpful', 'Helpful'),
        ('Indifferent', 'Indifferent'),
        ('Wary', 'Wary'),
        ('Enthusiastic', 'Enthusiastic'),
        ('Cautious', 'Cautious'),
        ('Welcoming', 'Welcoming'),
        ('Guarded', 'Guarded'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='npcs')
    name = models.CharField(max_length=120)
    npc_type = models.CharField(max_length=12, choices=NPC_TYPES, default='NEUTRAL')
    race = models.CharField(max_length=80, blank=True, null=True, help_text="Race (Human, Elf, Dwarf, etc.)")
    occupation = models.CharField(max_length=80, blank=True, null=True, help_text="Occupation (Blacksmith, Merchant, Guard, etc.)")
    
    # Social & Roleplay
    disposition = models.CharField(max_length=20, choices=DISPOSITION_CHOICES, blank=True, null=True, help_text="How they feel about the party")
    motivation = models.TextField(blank=True, null=True, help_text="What drives this NPC")
    secrets = models.TextField(blank=True, null=True, help_text="Secrets this NPC knows")
    location = models.CharField(max_length=200, blank=True, null=True, help_text="Where this NPC can be found")
    background = models.TextField(blank=True, null=True, help_text="Their history and role in the world")
    
    # Combat Stats (optional - only fill when needed)
    armor_class = models.PositiveIntegerField(blank=True, null=True, help_text="Armor Class (only if they might fight)")
    hit_points = models.PositiveIntegerField(blank=True, null=True, help_text="Hit Points (only if they might fight)")
    challenge_rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, help_text="Challenge Rating (only if they might fight)")
    speed = models.CharField(max_length=50, blank=True, null=True, help_text="Movement speed (e.g., '30 ft.')")
    
    # Optional Advanced Combat
    damage_resistances = models.CharField(max_length=200, blank=True, null=True, help_text="Damage resistances")
    condition_immunities = models.CharField(max_length=200, blank=True, null=True, help_text="Condition immunities")
    senses = models.CharField(max_length=200, blank=True, null=True, help_text="Special senses")
    actions = models.TextField(blank=True, null=True, help_text="Combat actions they can take")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['npc_type', 'name']
        verbose_name = 'NPC'
        verbose_name_plural = 'NPCs'
    
    def __str__(self):
        return f"{self.name} ({self.get_npc_type_display()})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('npcs:npc_detail', kwargs={'pk': self.pk})
    
    @property
    def is_combat_ready(self):
        """Check if NPC has essential combat stats"""
        return self.armor_class is not None and self.hit_points is not None
    
    @property
    def is_friendly(self):
        """Check if NPC is friendly to the party"""
        return self.npc_type in ['ALLY', 'MERCHANT', 'QUESTGIVER', 'INFORMATION']
    
    @property
    def is_hostile(self):
        """Check if NPC is hostile to the party"""
        return self.npc_type == 'ENEMY'
    
    @property
    def challenge_rating_display(self):
        """Display challenge rating in a readable format"""
        if not self.challenge_rating:
            return None
        cr = float(self.challenge_rating)
        if cr == 0.25:
            return "1/4"
        elif cr == 0.5:
            return "1/2"
        else:
            return str(int(cr)) if cr == int(cr) else str(cr)