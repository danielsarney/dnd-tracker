"""
Monster Models for D&D Tracker

This module defines the Monster model which represents creatures and enemies
that can be used in D&D encounters. The model stores comprehensive monster
statistics including ability scores, combat features, and special abilities.

Key Features:
- Complete monster statistics (AC, HP, speed, ability scores)
- Combat features (resistances, immunities, vulnerabilities)
- Special abilities (traits, actions, bonus actions, reactions)
- Challenge rating and gear information
"""

from django.db import models


class Monster(models.Model):
    """
    Model representing a monster or creature in D&D.

    This model stores all the statistical and mechanical information about
    a monster that would be found in a D&D monster manual. It includes
    basic stats, ability scores, combat features, and special abilities.

    Attributes:
        name: The name of the monster
        ac: Armor Class
        initiative: Initiative bonus (e.g., "+16")
        hp: Hit Points with dice notation (e.g., "333 (29d10 + 174)")
        speed: Movement speeds (e.g., "40 ft, Swim 10ft")
        strength/dexterity/constitution/intelligence/wisdom/charisma: Ability scores
        strength_mod/dexterity_mod/etc: Ability modifiers
        strength_save/dexterity_save/etc: Saving throw bonuses
        skills: Skills and proficiencies
        resistances: Damage resistances
        immunities: Damage immunities
        vulnerabilities: Damage vulnerabilities
        senses: Special senses (e.g., "darkvision 60ft")
        languages: Languages the monster knows
        gear: Equipment, weapons, armor, and other gear
        challenge_rating: Challenge Rating (e.g., "CR 20")
        traits: Special traits and abilities
        actions: Standard actions
        bonus_actions: Bonus actions
        reactions: Reactions
        legendary_actions: Legendary actions (for legendary creatures)
    """

    # Basic Information
    name = models.CharField(
        max_length=200, help_text="The name of the monster or creature"
    )
    ac = models.PositiveIntegerField(help_text="Armor Class")
    initiative = models.CharField(
        max_length=50, help_text="Initiative bonus (e.g., '+16')"
    )
    hp = models.CharField(
        max_length=100,
        help_text="Hit Points with dice notation (e.g., '333 (29d10 + 174)')",
    )
    speed = models.CharField(
        max_length=200, help_text="Movement speeds (e.g., '40 ft, Swim 10ft')"
    )

    # Ability Scores - Strength
    strength = models.CharField(
        max_length=50, help_text="Strength score (e.g., '24 +7')"
    )
    strength_mod = models.CharField(
        max_length=20, help_text="Strength Modifier (e.g., '+7')", default="+0"
    )
    strength_save = models.CharField(
        max_length=20, help_text="Strength Saving Throw (e.g., '+7')", default="+0"
    )

    # Ability Scores - Dexterity
    dexterity = models.CharField(
        max_length=50, help_text="Dexterity score (e.g., '19 +4')"
    )
    dexterity_mod = models.CharField(
        max_length=20, help_text="Dexterity Modifier (e.g., '+4')", default="+0"
    )
    dexterity_save = models.CharField(
        max_length=20, help_text="Dexterity Saving Throw (e.g., '+4')", default="+0"
    )

    # Ability Scores - Constitution
    constitution = models.CharField(max_length=50, help_text="Constitution score")
    constitution_mod = models.CharField(
        max_length=20, help_text="Constitution Modifier", default="+0"
    )
    constitution_save = models.CharField(
        max_length=20, help_text="Constitution Saving Throw", default="+0"
    )

    # Ability Scores - Intelligence
    intelligence = models.CharField(max_length=50, help_text="Intelligence score")
    intelligence_mod = models.CharField(
        max_length=20, help_text="Intelligence Modifier", default="+0"
    )
    intelligence_save = models.CharField(
        max_length=20, help_text="Intelligence Saving Throw", default="+0"
    )

    # Ability Scores - Wisdom
    wisdom = models.CharField(max_length=50, help_text="Wisdom score")
    wisdom_mod = models.CharField(
        max_length=20, help_text="Wisdom Modifier", default="+0"
    )
    wisdom_save = models.CharField(
        max_length=20, help_text="Wisdom Saving Throw", default="+0"
    )

    # Ability Scores - Charisma
    charisma = models.CharField(max_length=50, help_text="Charisma score")
    charisma_mod = models.CharField(
        max_length=20, help_text="Charisma Modifier", default="+0"
    )
    charisma_save = models.CharField(
        max_length=20, help_text="Charisma Saving Throw", default="+0"
    )

    # Combat Features
    skills = models.TextField(
        blank=True, null=True, help_text="Skills and proficiencies"
    )
    resistances = models.TextField(
        blank=True, null=True, help_text="Damage resistances"
    )
    immunities = models.TextField(blank=True, null=True, help_text="Damage immunities")
    vulnerabilities = models.TextField(
        blank=True, null=True, help_text="Damage vulnerabilities"
    )
    senses = models.TextField(
        blank=True, null=True, help_text="Special senses (e.g., 'darkvision 60ft')"
    )
    languages = models.TextField(
        blank=True, null=True, help_text="Languages the monster knows"
    )
    gear = models.TextField(
        blank=True, null=True, help_text="Equipment, weapons, armor, and other gear"
    )
    challenge_rating = models.CharField(
        max_length=20, help_text="Challenge Rating (e.g., 'CR 20')"
    )

    # Actions and Abilities
    traits = models.TextField(
        blank=True, null=True, help_text="Special traits and abilities"
    )
    actions = models.TextField(blank=True, null=True, help_text="Standard actions")
    bonus_actions = models.TextField(blank=True, null=True, help_text="Bonus actions")
    reactions = models.TextField(blank=True, null=True, help_text="Reactions")
    legendary_actions = models.TextField(
        blank=True, null=True, help_text="Legendary actions (for legendary creatures)"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        """String representation of the monster"""
        return self.name
