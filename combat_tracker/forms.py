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
