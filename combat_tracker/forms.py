from django import forms
from .models import CombatEncounter, CombatParticipant
from campaigns.models import Campaign
from players.models import Player
from npcs.models import NPC
from monsters.models import Monster


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
    
    # Character type selection
    CHARACTER_TYPE_CHOICES = [
        ('', 'Select character type...'),
        ('player', 'Player Character'),
        ('npc', 'NPC'),
        ('monster', 'Monster'),
        ('custom', 'Custom Participant'),
    ]
    
    character_type = forms.ChoiceField(
        choices=CHARACTER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'updateCharacterOptions(this)'
        })
    )
    
    # Character selection fields
    player = forms.ModelChoiceField(
        queryset=Player.objects.none(),
        required=False,
        empty_label="Select a player...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    npc = forms.ModelChoiceField(
        queryset=NPC.objects.none(),
        required=False,
        empty_label="Select an NPC...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    monster = forms.ModelChoiceField(
        queryset=Monster.objects.none(),
        required=False,
        empty_label="Select a monster...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    
    class Meta:
        model = CombatParticipant
        fields = [
            'character_type', 'player', 'npc', 'monster', 'name', 'initiative_roll',
            'armor_class', 'hit_points', 'max_hit_points', 'speed', 'challenge_rating',
            'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma',
            'strength_save', 'dexterity_save', 'constitution_save', 'intelligence_save', 'wisdom_save', 'charisma_save',
            'skills', 'damage_resistances', 'damage_immunities', 'condition_immunities', 'senses',
            'multiattack', 'actions', 'bonus_actions', 'reactions', 'legendary_actions'
        ]
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
            }),
            'armor_class': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Armor Class (can be modified by spells)'
            }),
            'hit_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Current HP (can go negative)'
            }),
            'max_hit_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Max HP'
            }),
            'speed': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 30 ft.'
            }),
            'challenge_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.25',
                'min': '0',
                'placeholder': 'e.g., 0.25, 0.5, 1, 2'
            }),
            'strength': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30'
            }),
            'dexterity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30'
            }),
            'constitution': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30'
            }),
            'intelligence': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30'
            }),
            'wisdom': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30'
            }),
            'charisma': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30'
            }),
            'strength_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +3'
            }),
            'dexterity_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +3'
            }),
            'constitution_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +3'
            }),
            'intelligence_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +3'
            }),
            'wisdom_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +3'
            }),
            'charisma_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +3'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'e.g., Perception +4, Stealth +6'
            }),
            'damage_resistances': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., fire, cold'
            }),
            'damage_immunities': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., fire, poison'
            }),
            'condition_immunities': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., charmed, frightened'
            }),
            'senses': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., darkvision 60 ft.'
            }),
            'multiattack': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Multiattack description...'
            }),
            'actions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Actions the creature can take...'
            }),
            'bonus_actions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Bonus actions...'
            }),
            'reactions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Reactions...'
            }),
            'legendary_actions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Legendary actions...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        campaign = kwargs.pop('campaign', None)
        super().__init__(*args, **kwargs)
        
        if campaign:
            # Set up querysets for each character type
            self.fields['player'].queryset = Player.objects.filter(campaign=campaign)
            self.fields['npc'].queryset = NPC.objects.filter(campaign=campaign)
            self.fields['monster'].queryset = Monster.objects.filter(campaign=campaign)
    
    def clean(self):
        cleaned_data = super().clean()
        character_type = cleaned_data.get('character_type')
        player = cleaned_data.get('player')
        npc = cleaned_data.get('npc')
        monster = cleaned_data.get('monster')
        name = cleaned_data.get('name')
        
        # Validate that the appropriate character is selected based on type
        if character_type == 'player' and not player:
            raise forms.ValidationError("Please select a player character.")
        elif character_type == 'npc' and not npc:
            raise forms.ValidationError("Please select an NPC.")
        elif character_type == 'monster' and not monster:
            raise forms.ValidationError("Please select a monster.")
        elif character_type == 'custom' and not name:
            raise forms.ValidationError("Please enter a name for the custom participant.")
        
        # Set the name based on the selected character
        if character_type == 'player' and player:
            cleaned_data['name'] = player.character_name
        elif character_type == 'npc' and npc:
            cleaned_data['name'] = npc.name
        elif character_type == 'monster' and monster:
            cleaned_data['name'] = monster.name
        
        return cleaned_data


