from django import forms
from .models import Encounter
from campaigns.models import Campaign
from players.models import Player
from monsters.models import Monster


class EncounterForm(forms.ModelForm):
    class Meta:
        model = Encounter
        fields = ["name", "description", "campaign", "players", "monsters"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter encounter name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the encounter",
                }
            ),
            "campaign": forms.Select(attrs={"class": "form-control"}),
            "players": forms.CheckboxSelectMultiple(),
            "monsters": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["campaign"].required = True
        self.fields["players"].required = True
        self.fields["monsters"].required = True

        # Set querysets
        self.fields["campaign"].queryset = Campaign.objects.all()
        self.fields["players"].queryset = Player.objects.all()
        self.fields["monsters"].queryset = Monster.objects.all()

        # Add CSS classes for checkboxes
        self.fields["players"].widget.attrs.update({"class": "form-check-input"})
        self.fields["monsters"].widget.attrs.update({"class": "form-check-input"})


class InitiativeForm(forms.Form):
    """Form for entering initiative rolls for all participants"""

    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add initiative fields for players
        for player in encounter.players.all():
            field_name = f"player_{player.id}_initiative"
            self.fields[field_name] = forms.IntegerField(
                label=f"{player.character_name} ({player.player_name})",
                min_value=1,
                max_value=30,
                widget=forms.NumberInput(
                    attrs={"class": "form-control", "placeholder": "Roll initiative"}
                ),
            )

        # Add initiative fields for monsters
        for monster in encounter.monsters.all():
            field_name = f"monster_{monster.id}_initiative"
            self.fields[field_name] = forms.IntegerField(
                label=f"{monster.name}",
                min_value=1,
                max_value=30,
                widget=forms.NumberInput(
                    attrs={"class": "form-control", "placeholder": "Roll initiative"}
                ),
            )


class HPTrackingForm(forms.Form):
    """Form for tracking HP changes (damage/healing)"""

    HP_CHANGE_TYPE_CHOICES = [
        ("damage", "Damage"),
        ("healing", "Healing"),
    ]

    change_type = forms.ChoiceField(
        choices=HP_CHANGE_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    amount = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter amount"}
        ),
    )
    notes = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Optional notes (e.g., 'Fireball', 'Cure Wounds')",
            }
        ),
    )
