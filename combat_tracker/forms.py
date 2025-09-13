from django import forms
from .models import CombatEncounter, CombatParticipant
from campaigns.models import Campaign
from characters.models import Character


class CombatEncounterForm(forms.ModelForm):
    """Form for creating/editing combat encounters"""
    
    class Meta:
        model = CombatEncounter
        fields = ['campaign', 'name']
        widgets = {
            'campaign': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select a campaign'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter encounter name (e.g., Goblin Ambush)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class CombatParticipantForm(forms.ModelForm):
    """Form for adding participants to combat encounters"""
    
    character = forms.ModelChoiceField(
        queryset=Character.objects.none(),
        required=False,
        empty_label="Select a character (optional)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = CombatParticipant
        fields = ['character', 'name', 'initiative_roll']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter participant name'
            }),
            'initiative_roll': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '50',
                'placeholder': 'Total initiative (e.g., 18)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        campaign = kwargs.pop('campaign', None)
        super().__init__(*args, **kwargs)
        
        if campaign:
            self.fields['character'].queryset = Character.objects.filter(campaign=campaign)
            # Update the widget to show character type in the dropdown
            self.fields['character'].widget.attrs['onchange'] = 'updateCharacterName(this)'
    
    def clean(self):
        cleaned_data = super().clean()
        character = cleaned_data.get('character')
        name = cleaned_data.get('name')
        
        # If no character is selected, name is required
        if not character and not name:
            raise forms.ValidationError("Either select a character or enter a custom name.")
        
        # If character is selected, use character's name
        if character:
            cleaned_data['name'] = character.name
        
        return cleaned_data


