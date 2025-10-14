from django.db import models
from campaigns.models import Campaign
from players.models import Player
from monsters.models import Monster


class Encounter(models.Model):
    name = models.CharField(max_length=200, help_text="Encounter name")
    description = models.TextField(
        blank=True, null=True, help_text="Encounter description"
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="encounters",
        help_text="Associated campaign",
    )
    players = models.ManyToManyField(
        Player,
        related_name="encounters",
        help_text="Players participating in this encounter",
    )
    monsters = models.ManyToManyField(
        Monster,
        related_name="encounters",
        help_text="Monsters in this encounter",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.campaign.title})"


class CombatSession(models.Model):
    encounter = models.OneToOneField(
        Encounter,
        on_delete=models.CASCADE,
        related_name="combat_session",
        help_text="The encounter this combat session belongs to",
    )
    current_round = models.PositiveIntegerField(default=1, help_text="Current combat round")
    current_turn_index = models.PositiveIntegerField(default=0, help_text="Index of current turn in initiative order")
    is_active = models.BooleanField(default=True, help_text="Whether combat is currently active")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True, help_text="When combat ended")

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Combat: {self.encounter.name} - Round {self.current_round}"


class CombatParticipant(models.Model):
    PARTICIPANT_TYPE_CHOICES = [
        ('player', 'Player'),
        ('monster', 'Monster'),
    ]
    
    combat_session = models.ForeignKey(
        CombatSession,
        on_delete=models.CASCADE,
        related_name="participants",
        help_text="The combat session this participant belongs to",
    )
    participant_type = models.CharField(
        max_length=10,
        choices=PARTICIPANT_TYPE_CHOICES,
        help_text="Whether this is a player or monster"
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Player character (if participant_type is 'player')"
    )
    monster = models.ForeignKey(
        Monster,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Monster (if participant_type is 'monster')"
    )
    initiative = models.IntegerField(help_text="Initiative roll result")
    current_hp = models.IntegerField(help_text="Current hit points")
    max_hp = models.IntegerField(help_text="Maximum hit points")
    is_dead = models.BooleanField(default=False, help_text="Whether this participant is dead/unconscious")
    turn_completed = models.BooleanField(default=False, help_text="Whether current turn is completed")

    class Meta:
        ordering = ["-initiative", "participant_type"]

    def __str__(self):
        if self.participant_type == 'player':
            return f"{self.player.character_name} (Initiative: {self.initiative})"
        else:
            return f"{self.monster.name} (Initiative: {self.initiative})"

    @property
    def name(self):
        """Get the name of the participant"""
        if self.participant_type == 'player':
            return self.player.character_name
        else:
            return self.monster.name

    @property
    def ac(self):
        """Get the AC of the participant"""
        if self.participant_type == 'player':
            return self.player.ac
        else:
            return self.monster.ac
