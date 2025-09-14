from django import forms
from .models import Monster


class MonsterForm(forms.ModelForm):
    class Meta:
        model = Monster
        fields = [
            'name', 'monster_type', 'size', 'alignment', 'challenge_rating',
            'armor_class', 'hit_points', 'speed',
            'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma',
            'strength_save', 'dexterity_save', 'constitution_save', 'intelligence_save', 'wisdom_save', 'charisma_save',
            'skills', 'damage_resistances', 'damage_immunities', 'condition_immunities', 'senses', 'languages',
            'multiattack', 'actions', 'bonus_actions', 'reactions', 'legendary_actions'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter monster name'
            }),
            'monster_type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select monster type'
            }),
            'size': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select size'
            }),
            'alignment': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Lawful Evil, Chaotic Good'
            }),
            'challenge_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.25',
                'min': '0',
                'placeholder': 'e.g., 0.25, 0.5, 1, 2, etc.'
            }),
            'armor_class': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'hit_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'speed': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 30 ft., fly 60 ft.'
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
                'placeholder': 'e.g., bludgeoning, piercing, and slashing from nonmagical attacks'
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
                'placeholder': 'e.g., darkvision 60 ft., passive Perception 12'
            }),
            'languages': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Common, Orcish, Draconic'
            }),
            'multiattack': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Multiattack description...'
            }),
            'actions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Actions the monster can take...'
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
                'placeholder': 'Legendary actions (if any)...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
