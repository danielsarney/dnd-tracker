from django.db import models
from django.core.exceptions import ValidationError


class Campaign(models.Model):
    title = models.CharField(
        max_length=200, blank=False, null=False, help_text="Campaign title"
    )
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

    def clean(self):
        super().clean()
        if not self.title or not self.title.strip():
            raise ValidationError({"title": "Title cannot be empty."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
