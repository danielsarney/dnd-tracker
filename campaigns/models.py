"""
Campaign Models for D&D Tracker

This module defines the Campaign model which represents a D&D campaign
in the tracker application. Campaigns serve as containers for players,
sessions, encounters, and other campaign-related data.

Key Features:
- Campaign title and description management
- Introduction and character requirements storage
- Data validation to ensure campaign integrity
"""

from django.db import models
from django.core.exceptions import ValidationError


class Campaign(models.Model):
    """
    Model representing a D&D campaign.

    A campaign is the central organizing unit in the D&D Tracker application.
    It contains all the information about a specific D&D campaign including
    its title, description, introduction, and character requirements.
    Campaigns are linked to players, sessions, and encounters.

    Attributes:
        title: The name/title of the campaign (required)
        description: Detailed description of the campaign setting and story
        introduction: Introduction text for new players joining the campaign
        character_requirements: Guidelines for character creation and restrictions
    """

    title = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        help_text="The name or title of the campaign",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the campaign setting, story, and world",
    )
    introduction = models.TextField(
        blank=True,
        null=True,
        help_text="Introduction text for new players joining the campaign",
    )
    character_requirements = models.TextField(
        blank=True,
        null=True,
        help_text="Guidelines for character creation, restrictions, and requirements",
    )

    class Meta:
        ordering = ["title"]

    def clean(self):
        """
        Validate the campaign data before saving.

        This method ensures that the campaign has a valid title before
        it can be saved to the database. It raises a ValidationError
        if the title is empty or contains only whitespace.

        Raises:
            ValidationError: If the title is empty or invalid
        """
        super().clean()
        if not self.title or not self.title.strip():
            raise ValidationError({"title": "Title cannot be empty."})

    def save(self, *args, **kwargs):
        """
        Save the campaign instance with validation.

        This method calls the clean() method to validate the data
        before saving to ensure data integrity.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of the campaign"""
        return self.title
