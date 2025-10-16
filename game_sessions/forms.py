"""
Game Session Forms for D&D Tracker

This module contains Django forms for game session management including
creation, editing, and validation of session data.

Key Features:
- Game session creation and editing forms
- Bootstrap styling for form fields
- Field validation and requirements
- User-friendly placeholders and widgets
- Campaign selection dropdown
- Date picker for session dates
"""

from django import forms
from .models import Session


class SessionForm(forms.ModelForm):
    """
    Form for creating and editing D&D game sessions.

    This form handles all session data including campaign association,
    planning notes, session notes, and session date. It provides Bootstrap
    styling and appropriate widgets for each field type.
    """

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
        """
        Initialize form with field requirements.

        Sets campaign as required while making other fields optional
        to allow for flexible session creation and note-taking.
        """
        super().__init__(*args, **kwargs)
        self.fields["campaign"].required = True
        self.fields["session_date"].required = False
        self.fields["planning_notes"].required = False
        self.fields["session_notes"].required = False
