from django.db import models


class Campaign(models.Model):
    title = models.CharField(max_length=200, help_text="Campaign title")
    description = models.TextField(
        blank=True, null=True, help_text="Campaign description"
    )
    introduction = models.TextField(
        blank=True, null=True, help_text="Campaign introduction"
    )
    character_requirements = models.TextField(
        blank=True, null=True, help_text="Character requirements"
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
