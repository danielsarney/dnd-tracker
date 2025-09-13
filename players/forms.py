from django import forms
from .models import Player


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['campaign', 'character_name', 'player_name', 'background', 'level', 'armor_class']
        widgets = {
            'campaign': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select a campaign'
            }),
            'character_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter character name'
            }),
            'player_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter real-life player name'
            }),
            'background': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your character\'s background for story integration...'
            }),
            'level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20',
                'placeholder': 'Character level'
            }),
            'armor_class': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Armor Class'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
