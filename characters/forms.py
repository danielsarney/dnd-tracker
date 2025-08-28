from django import forms
from .models import Character


class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['campaign', 'type', 'name', 'race', 'character_class', 'background']
        widgets = {
            'campaign': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select a campaign'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select character type'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter character name'
            }),
            'race': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter character race'
            }),
            'character_class': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter character class'
            }),
            'background': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your character\'s background...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
