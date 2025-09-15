from django import forms
from .models import NPC


class NPCForm(forms.ModelForm):
    class Meta:
        model = NPC
        fields = [
            'name', 'race', 'occupation', 'size', 'location', 'background',
            'armor_class', 'hit_points', 'level', 'speed',
            'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma',
            'strength_save', 'dexterity_save', 'constitution_save', 
            'intelligence_save', 'wisdom_save', 'charisma_save',
            'skills', 'damage_resistances', 'damage_immunities', 'condition_immunities', 
            'senses', 'languages', 'multiattack', 'actions', 'bonus_actions', 
            'reactions', 'legendary_actions'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter NPC name'
            }),
            'race': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Human, Elf, Dwarf'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Blacksmith, Merchant, Guard'
            }),
            'size': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Where can this NPC be found?'
            }),
            'background': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Their history and role in the world...'
            }),
            'armor_class': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Armor Class'
            }),
            'hit_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Hit Points'
            }),
            'level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20',
                'placeholder': 'e.g., 1, 5, 10, 20'
            }),
            'speed': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 30 ft.'
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
                'placeholder': 'Saving throw bonus'
            }),
            'dexterity_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Saving throw bonus'
            }),
            'constitution_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Saving throw bonus'
            }),
            'intelligence_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Saving throw bonus'
            }),
            'wisdom_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Saving throw bonus'
            }),
            'charisma_save': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Saving throw bonus'
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
                'placeholder': 'e.g., poison'
            }),
            'condition_immunities': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., charmed, frightened'
            }),
            'senses': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., darkvision 60 ft.'
            }),
            'languages': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Common, Elvish'
            }),
            'multiattack': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Multiattack description'
            }),
            'actions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Actions the NPC can take...'
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
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
