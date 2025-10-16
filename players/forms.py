"""
Player Character Forms for D&D Tracker

This module contains Django forms for player character management including
creation, editing, and validation of character data.

Key Features:
- Player character creation and editing forms
- Bootstrap styling for form fields
- Field validation and requirements
- User-friendly placeholders and widgets
- Campaign selection dropdown
"""

from django import forms
from .models import Player


class PlayerForm(forms.ModelForm):
    """
    Form for creating and editing D&D player characters.

    This form handles all player character data including character name,
    player name, class, race, level, armor class, background, and campaign
    association. It provides Bootstrap styling and appropriate widgets
    for each field type.
    """

    class Meta:
        model = Player
        fields = [
            "character_name",
            "player_name",
            "character_class",
            "subclass",
            "race",
            "level",
            "ac",
            "background",
            "campaign",
        ]
        widgets = {
            "character_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter character name"}
            ),
            "player_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter player's real name",
                }
            ),
            "character_class": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter character class (e.g., Wizard/Monk)",
                }
            ),
            "subclass": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter subclass (e.g., Beast Master, Eldritch Knight)",
                }
            ),
            "race": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter character race",
                }
            ),
            "level": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "max": "20",
                    "placeholder": "1",
                }
            ),
            "ac": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "placeholder": "10"}
            ),
            "background": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter character background story",
                }
            ),
            "campaign": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize form with field requirements.

        Sets required fields for character creation while making subclass
        optional since not all characters have subclasses.
        """
        super().__init__(*args, **kwargs)
        self.fields["character_name"].required = True
        self.fields["player_name"].required = True
        self.fields["character_class"].required = True
        self.fields["subclass"].required = False
        self.fields["race"].required = True
        self.fields["level"].required = True
        self.fields["ac"].required = True
        self.fields["background"].required = True
        self.fields["campaign"].required = True
