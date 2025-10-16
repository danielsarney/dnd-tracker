"""
Player Character Models for D&D Tracker

This module defines the Player model which represents player characters
in D&D campaigns. Each player character belongs to a specific campaign
and contains all the essential character information needed for gameplay.

Key Features:
- Character and player name tracking
- Character class and subclass information
- Race, level, and armor class storage
- Character background and campaign association
"""

from django.db import models
from campaigns.models import Campaign


class Player(models.Model):
    """
    Model representing a player character in a D&D campaign.

    This model stores all the essential information about a player character
    including their name, class, race, level, and other gameplay-relevant
    statistics. Each player character must be associated with a campaign.

    Attributes:
        character_name: The name of the character in the game
        player_name: The real name of the person playing this character
        character_class: The character's class (e.g., Wizard, Fighter, Rogue)
        subclass: The character's subclass (e.g., Beast Master, Eldritch Knight)
        race: The character's race (e.g., Human, Elf, Dragonborn)
        level: The character's current level (defaults to 1)
        ac: The character's Armor Class
        background: The character's background story and history
        campaign: The campaign this character belongs to
    """

    character_name = models.CharField(
        max_length=100, help_text="The name of the character in the game world"
    )
    player_name = models.CharField(
        max_length=100, help_text="The real name of the person playing this character"
    )
    character_class = models.CharField(
        max_length=100,
        help_text="The character's class (e.g., Wizard, Fighter, Rogue, Monk)",
    )
    subclass = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="The character's subclass (e.g., Beast Master, Eldritch Knight, Way of Shadow)",
    )
    race = models.CharField(
        max_length=100,
        help_text="The character's race (e.g., Human, Elf, Dragonborn, Tiefling)",
    )
    level = models.PositiveIntegerField(
        default=1, help_text="The character's current level"
    )
    ac = models.PositiveIntegerField(help_text="The character's Armor Class (AC)")
    background = models.TextField(
        help_text="The character's background story, history, and personality"
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="players",
        help_text="The campaign this character belongs to",
    )

    class Meta:
        ordering = ["character_name"]

    def __str__(self):
        """String representation showing character name and player name"""
        return f"{self.character_name} ({self.player_name})"
