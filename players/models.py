from django.db import models
from campaigns.models import Campaign


class Player(models.Model):
    character_name = models.CharField(max_length=100, help_text="Character name")
    player_name = models.CharField(max_length=100, help_text="Player's real name")
    character_class = models.CharField(
        max_length=100, help_text="Character class (e.g., Wizard/Monk)"
    )
    subclass = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Character subclass (e.g., Beast Master, Eldritch Knight)",
    )
    race = models.CharField(max_length=100, help_text="Character race")
    level = models.PositiveIntegerField(default=1, help_text="Character level")
    ac = models.PositiveIntegerField(help_text="Armor Class")
    background = models.TextField(help_text="Character background")
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="players",
        help_text="Associated campaign",
    )

    class Meta:
        ordering = ["character_name"]

    def __str__(self):
        return f"{self.character_name} ({self.player_name})"
