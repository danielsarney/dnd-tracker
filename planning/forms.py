from django import forms
from .models import PlanningSession


class PlanningSessionForm(forms.ModelForm):
    class Meta:
        model = PlanningSession
        fields = ['campaign', 'session_date', 'title', 'notes']
        widgets = {
            'campaign': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select a campaign'
            }),
            'session_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Select session date'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a title for this planning session'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Enter your preparation notes for this session...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default date to today for new planning sessions
        if not self.instance.pk:  # Only for new instances, not when editing
            from django.utils import timezone
            self.fields['session_date'].initial = timezone.now().date()
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
