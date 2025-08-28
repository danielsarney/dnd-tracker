from django import forms
from .models import GameSession


class GameSessionForm(forms.ModelForm):
    class Meta:
        model = GameSession
        fields = ['campaign', 'date', 'summary']
        widgets = {
            'campaign': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select a campaign'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Select session date'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Describe what happened in this session...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
