from django.db import models
from campaigns.models import Campaign
from characters.models import Character


class CombatEncounter(models.Model):
    """Represents a combat encounter within a campaign"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='combat_encounters')
    name = models.CharField(max_length=120, help_text="Name of the encounter (e.g., 'Goblin Ambush')")
    is_active = models.BooleanField(default=False, help_text="Whether this encounter is currently active")
    current_round = models.PositiveIntegerField(default=1)
    current_turn = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.campaign.name})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('combat_tracker:encounter_detail', kwargs={'pk': self.pk})
    
    def get_participants(self):
        """Get all participants ordered by initiative (highest first)"""
        return self.participants.all().order_by('-initiative_roll')
    
    def get_current_participant(self):
        """Get the participant whose turn it currently is"""
        participants = list(self.get_participants())
        if participants and self.current_turn < len(participants):
            return participants[self.current_turn]
        return None
    
    def next_turn(self):
        """Move to the next turn"""
        participants = list(self.get_participants())
        if not participants:
            return False
        
        self.current_turn += 1
        if self.current_turn >= len(participants):
            # End of round, start new round
            self.current_round += 1
            self.current_turn = 0
        self.save()
        return True
    
    def reset_encounter(self):
        """Reset the encounter to round 1, turn 0"""
        self.current_round = 1
        self.current_turn = 0
        self.is_active = False
        self.save()


class CombatParticipant(models.Model):
    """Represents a participant in a combat encounter"""
    encounter = models.ForeignKey(CombatEncounter, on_delete=models.CASCADE, related_name='participants')
    character = models.ForeignKey(Character, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=120, help_text="Name of the participant")
    initiative_roll = models.PositiveIntegerField(help_text="Total initiative value")
    is_turn_complete = models.BooleanField(default=False, help_text="Whether this participant has completed their turn")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-initiative_roll']
    
    def __str__(self):
        return f"{self.name} (Initiative: {self.initiative_roll})"
    
    @property
    def total_initiative(self):
        """Get total initiative value"""
        return self.initiative_roll
    
    def get_character_type_display(self):
        """Get the character type for display purposes"""
        if self.character:
            return self.character.get_type_display()
        return "Custom"