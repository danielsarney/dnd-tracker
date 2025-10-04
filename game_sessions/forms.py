from django import forms
from .models import Session


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            "campaign",
            "planning_notes",
            "session_notes",
            "session_date",
        ]
        widgets = {
            "campaign": forms.Select(attrs={"class": "form-control"}),
            "planning_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Enter your pre-session planning notes...",
                }
            ),
            "session_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Enter notes from during or after the session...",
                }
            ),
            "session_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["campaign"].required = True
        self.fields["session_date"].required = False
        self.fields["planning_notes"].required = False
        self.fields["session_notes"].required = False
