"""
Game Session Models for D&D Tracker

This module defines the Session model which represents individual game sessions
within a D&D campaign. Sessions contain planning notes, session notes, and
tracking information for each play session.

Key Features:
- Session planning and note-taking
- Date tracking for sessions
- Campaign association
- Chronological ordering
"""

from django.db import models
from campaigns.models import Campaign


class Session(models.Model):
    """
    Model representing a single game session in a D&D campaign.

    This model stores information about individual play sessions including
    planning notes prepared before the session and notes taken during or
    after the session. Each session is associated with a specific campaign.

    Attributes:
        campaign: The campaign this session belongs to
        planning_notes: Pre-session planning notes and preparation
        session_notes: Notes taken during or after the session
        session_date: The date when the session took place
    """

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text="The campaign this session belongs to",
    )
    planning_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Pre-session planning notes, preparation, and DM notes",
    )
    session_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes taken during or after the session, including what happened",
    )
    session_date = models.DateField(
        blank=True, null=True, help_text="The date when this session took place"
    )

    class Meta:
        ordering = ["-session_date", "campaign__title"]

    def __str__(self):
        """String representation showing campaign and session date"""
        return f"{self.campaign.title} - {self.session_date}"
