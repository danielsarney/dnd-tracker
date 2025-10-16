"""
Campaign Forms for D&D Tracker

This module contains Django forms for campaign management including
creation, editing, and validation of campaign data.

Key Features:
- Campaign creation and editing forms
- Bootstrap styling for form fields
- Field validation and requirements
- User-friendly placeholders and widgets
"""

from django import forms
from .models import Campaign


class CampaignForm(forms.ModelForm):
    """
    Form for creating and editing D&D campaigns.

    This form handles all campaign-related data including title, description,
    introduction, and character requirements. It provides Bootstrap styling
    and appropriate widgets for each field type.
    """

    class Meta:
        model = Campaign
        fields = ["title", "description", "introduction", "character_requirements"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter campaign title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe your campaign",
                }
            ),
            "introduction": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Campaign introduction",
                }
            ),
            "character_requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Character requirements",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize form with field requirements.

        Sets the title as required while making other fields optional
        to allow for flexible campaign creation.
        """
        super().__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["description"].required = False
        self.fields["introduction"].required = False
        self.fields["character_requirements"].required = False
