"""
Combat Tracker Models for D&D Tracker

This module defines models for managing combat encounters in D&D campaigns.
It includes models for encounters, combat sessions, and combat participants
to track initiative order, hit points, and turn management during combat.

Key Features:
- Encounter creation and management
- Combat session tracking with rounds and turns
- Initiative order management
- Hit point tracking for all participants
- Turn completion tracking
"""

from django.db import models
from campaigns.models import Campaign
from players.models import Player
from monsters.models import Monster


class Encounter(models.Model):
    """
    Model representing a combat encounter in a D&D campaign.

    An encounter defines a specific combat scenario with a name, description,
    and the participants involved (both players and monsters). Encounters
    can be created in advance and then activated as combat sessions.

    Attributes:
        name: The name of the encounter
        description: Detailed description of the encounter
        campaign: The campaign this encounter belongs to
        players: Player characters participating in this encounter
        monsters: Monsters involved in this encounter
        created_at: Timestamp when the encounter was created
        updated_at: Timestamp when the encounter was last modified
    """

    name = models.CharField(max_length=200, help_text="The name of the encounter")
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the encounter scenario",
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="encounters",
        help_text="The campaign this encounter belongs to",
    )
    players = models.ManyToManyField(
        Player,
        related_name="encounters",
        help_text="Player characters participating in this encounter",
    )
    monsters = models.ManyToManyField(
        Monster,
        related_name="encounters",
        help_text="Monsters involved in this encounter",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the encounter was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the encounter was last modified"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """String representation showing encounter name and campaign"""
        return f"{self.name} ({self.campaign.title})"


class CombatSession(models.Model):
    """
    Model representing an active combat session.

    A combat session is created when an encounter is started and tracks
    the current state of combat including the current round, whose turn
    it is, and whether combat is still active.

    Attributes:
        encounter: The encounter this combat session is based on
        current_round: The current combat round (starts at 1)
        current_turn_index: Index of current participant in initiative order
        is_active: Whether combat is currently ongoing
        started_at: Timestamp when combat began
        ended_at: Timestamp when combat ended (null if still active)
    """

    encounter = models.OneToOneField(
        Encounter,
        on_delete=models.CASCADE,
        related_name="combat_session",
        help_text="The encounter this combat session belongs to",
    )
    current_round = models.PositiveIntegerField(
        default=1, help_text="The current combat round"
    )
    current_turn_index = models.PositiveIntegerField(
        default=0, help_text="Index of current participant in initiative order"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether combat is currently active"
    )
    started_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when combat began"
    )
    ended_at = models.DateTimeField(
        null=True, blank=True, help_text="Timestamp when combat ended"
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        """String representation showing encounter and current round"""
        return f"Combat: {self.encounter.name} - Round {self.current_round}"


class CombatParticipant(models.Model):
    """
    Model representing a participant in an active combat session.

    This model tracks individual participants (both players and monsters)
    during combat, including their initiative order, current hit points,
    and turn status. Each participant is linked to either a Player or
    Monster model depending on their type.

    Attributes:
        combat_session: The combat session this participant belongs to
        participant_type: Whether this is a 'player' or 'monster'
        player: Player character (if participant_type is 'player')
        monster: Monster (if participant_type is 'monster')
        initiative: Initiative roll result for turn order
        current_hp: Current hit points
        max_hp: Maximum hit points
        is_dead: Whether this participant is dead/unconscious
        turn_completed: Whether current turn is completed
    """

    PARTICIPANT_TYPE_CHOICES = [
        ("player", "Player"),
        ("monster", "Monster"),
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
        help_text="Whether this is a player character or monster",
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Player character (if participant_type is 'player')",
    )
    monster = models.ForeignKey(
        Monster,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Monster (if participant_type is 'monster')",
    )
    initiative = models.IntegerField(help_text="Initiative roll result for turn order")
    current_hp = models.IntegerField(help_text="Current hit points")
    max_hp = models.IntegerField(help_text="Maximum hit points")
    is_dead = models.BooleanField(
        default=False, help_text="Whether this participant is dead or unconscious"
    )
    turn_completed = models.BooleanField(
        default=False, help_text="Whether the current turn is completed"
    )

    class Meta:
        ordering = ["-initiative", "participant_type"]

    def __str__(self):
        """String representation showing participant name and initiative"""
        if self.participant_type == "player":
            return f"{self.player.character_name} (Initiative: {self.initiative})"
        else:
            return f"{self.monster.name} (Initiative: {self.initiative})"

    @property
    def name(self):
        """
        Get the name of the participant.

        Returns the character name for players or monster name for monsters.

        Returns:
            str: The name of the participant
        """
        if self.participant_type == "player":
            return self.player.character_name
        else:
            return self.monster.name

    @property
    def ac(self):
        """
        Get the Armor Class of the participant.

        Returns the AC from the associated player or monster.

        Returns:
            int: The Armor Class of the participant
        """
        if self.participant_type == "player":
            return self.player.ac
        else:
            return self.monster.ac
