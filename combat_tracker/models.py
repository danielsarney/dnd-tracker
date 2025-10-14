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
