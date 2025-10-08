from django import forms
from .models import Monster


class MonsterForm(forms.ModelForm):
    class Meta:
        model = Monster
        fields = [
            "name",
            "ac",
            "initiative",
            "hp",
            "speed",
            "strength",
            "strength_mod",
            "strength_save",
            "dexterity",
            "dexterity_mod",
            "dexterity_save",
            "constitution",
            "constitution_mod",
            "constitution_save",
            "intelligence",
            "intelligence_mod",
            "intelligence_save",
            "wisdom",
            "wisdom_mod",
            "wisdom_save",
            "charisma",
            "charisma_mod",
            "charisma_save",
            "skills",
            "resistances",
            "immunities",
            "vulnerabilities",
            "senses",
            "languages",
            "gear",
            "challenge_rating",
            "traits",
            "actions",
            "bonus_actions",
            "reactions",
            "legendary_actions",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter monster name"}
            ),
            "ac": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "placeholder": "10"}
            ),
            "initiative": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+16"}
            ),
            "hp": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "333 (29d10 + 174)"}
            ),
            "speed": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "40 ft, Swim 10ft"}
            ),
            "strength": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "24"}
            ),
            "strength_mod": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+7"}
            ),
            "strength_save": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+7"}
            ),
            "dexterity": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "19"}
            ),
            "dexterity_mod": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+4"}
            ),
            "dexterity_save": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+4"}
            ),
            "constitution": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "22"}
            ),
            "constitution_mod": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+6"}
            ),
            "constitution_save": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+6"}
            ),
            "intelligence": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "18"}
            ),
            "intelligence_mod": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+4"}
            ),
            "intelligence_save": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+4"}
            ),
            "wisdom": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "16"}
            ),
            "wisdom_mod": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+3"}
            ),
            "wisdom_save": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+3"}
            ),
            "charisma": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "20"}
            ),
            "charisma_mod": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+5"}
            ),
            "charisma_save": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+5"}
            ),
            "skills": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Athletics +13, Perception +9, Stealth +7",
                }
            ),
            "resistances": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Fire, Cold, Lightning",
                }
            ),
            "immunities": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Poison, Charmed, Frightened",
                }
            ),
            "vulnerabilities": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Fire, Cold",
                }
            ),
            "senses": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Darkvision 120 ft, Passive Perception 19",
                }
            ),
            "languages": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Common, Draconic, Telepathy 120 ft",
                }
            ),
            "gear": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Plate Armor, Greatsword +3, Shield of Faith",
                }
            ),
            "challenge_rating": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "CR 20"}
            ),
            "traits": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Magic Resistance, Legendary Resistance (3/day)",
                }
            ),
            "actions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Multiattack. The dragon makes three attacks...",
                }
            ),
            "bonus_actions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Quick Strike. The dragon makes one attack...",
                }
            ),
            "reactions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Parry. The dragon adds 4 to its AC...",
                }
            ),
            "legendary_actions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "The dragon can take 3 legendary actions...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Required fields
        self.fields["name"].required = True
        self.fields["ac"].required = True
        self.fields["initiative"].required = True
        self.fields["hp"].required = True
        self.fields["speed"].required = True
        self.fields["strength"].required = True
        self.fields["strength_mod"].required = True
        self.fields["strength_save"].required = True
        self.fields["dexterity"].required = True
        self.fields["dexterity_mod"].required = True
        self.fields["dexterity_save"].required = True
        self.fields["constitution"].required = True
        self.fields["constitution_mod"].required = True
        self.fields["constitution_save"].required = True
        self.fields["intelligence"].required = True
        self.fields["intelligence_mod"].required = True
        self.fields["intelligence_save"].required = True
        self.fields["wisdom"].required = True
        self.fields["wisdom_mod"].required = True
        self.fields["wisdom_save"].required = True
        self.fields["charisma"].required = True
        self.fields["charisma_mod"].required = True
        self.fields["charisma_save"].required = True
        self.fields["challenge_rating"].required = True
