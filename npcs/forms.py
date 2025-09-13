from django import forms
from .models import NPC


class NPCForm(forms.ModelForm):
    class Meta:
        model = NPC
        fields = [
            'campaign', 'name', 'npc_type', 'race', 'occupation',
            'disposition', 'motivation', 'secrets', 'location', 'background',
            'armor_class', 'hit_points', 'challenge_rating', 'speed',
            'damage_resistances', 'condition_immunities', 'senses', 'actions'
        ]
        widgets = {
            'campaign': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select a campaign'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter NPC name'
            }),
            'npc_type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select NPC type'
            }),
            'race': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Human, Elf, Dwarf'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Blacksmith, Merchant, Guard'
            }),
            'disposition': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'How they feel about the party'
            }),
            'motivation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What drives this NPC?'
            }),
            'secrets': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What secrets does this NPC know?'
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
                'placeholder': 'Only if they might fight'
            }),
            'hit_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Only if they might fight'
            }),
            'challenge_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.25',
                'min': '0',
                'placeholder': 'e.g., 0.25, 0.5, 1, 2'
            }),
            'speed': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 30 ft.'
            }),
            'damage_resistances': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., fire, cold'
            }),
            'condition_immunities': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., charmed, frightened'
            }),
            'senses': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., darkvision 60 ft.'
            }),
            'actions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Combat actions they can take...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
