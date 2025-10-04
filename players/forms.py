from django import forms
from .models import Player


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = [
            "character_name",
            "player_name",
            "character_class",
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
        super().__init__(*args, **kwargs)
        self.fields["character_name"].required = True
        self.fields["player_name"].required = True
        self.fields["character_class"].required = True
        self.fields["race"].required = True
        self.fields["level"].required = True
        self.fields["ac"].required = True
        self.fields["background"].required = True
        self.fields["campaign"].required = True
