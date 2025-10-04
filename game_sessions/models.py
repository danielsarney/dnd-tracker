from django.db import models
from campaigns.models import Campaign


class Session(models.Model):
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text="Associated campaign",
    )
    planning_notes = models.TextField(
        blank=True, null=True, help_text="Pre-session planning notes"
    )
    session_notes = models.TextField(
        blank=True, null=True, help_text="During/post-session notes"
    )
    session_date = models.DateField(
        blank=True, null=True, help_text="Date of the session"
    )

    class Meta:
        ordering = ["-session_date", "campaign__title"]

    def __str__(self):
        return f"{self.campaign.title} - {self.session_date}"
