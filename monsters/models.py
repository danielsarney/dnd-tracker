from django.db import models


class Monster(models.Model):
    name = models.CharField(max_length=200, help_text="Monster name")
    ac = models.PositiveIntegerField(help_text="Armor Class")
    initiative = models.CharField(
        max_length=50, help_text="Initiative bonus (e.g., +16)"
    )
    hp = models.CharField(
        max_length=100, help_text="Hit Points (e.g., 333 (29d10 + 174))"
    )
    speed = models.CharField(max_length=200, help_text="Speed (e.g., 40 ft, Swim 10ft)")

    # Ability Scores
    strength = models.CharField(max_length=50, help_text="Strength (e.g., 24 +7)")
    strength_mod = models.CharField(
        max_length=20, help_text="Strength Modifier (e.g., +7)", default="+0"
    )
    strength_save = models.CharField(
        max_length=20, help_text="Strength Saving Throw (e.g., +7)", default="+0"
    )

    dexterity = models.CharField(max_length=50, help_text="Dexterity (e.g., 19 +4)")
    dexterity_mod = models.CharField(
        max_length=20, help_text="Dexterity Modifier (e.g., +4)", default="+0"
    )
    dexterity_save = models.CharField(
        max_length=20, help_text="Dexterity Saving Throw (e.g., +4)", default="+0"
    )

    constitution = models.CharField(max_length=50, help_text="Constitution")
    constitution_mod = models.CharField(
        max_length=20, help_text="Constitution Modifier", default="+0"
    )
    constitution_save = models.CharField(
        max_length=20, help_text="Constitution Saving Throw", default="+0"
    )

    intelligence = models.CharField(max_length=50, help_text="Intelligence")
    intelligence_mod = models.CharField(
        max_length=20, help_text="Intelligence Modifier", default="+0"
    )
    intelligence_save = models.CharField(
        max_length=20, help_text="Intelligence Saving Throw", default="+0"
    )

    wisdom = models.CharField(max_length=50, help_text="Wisdom")
    wisdom_mod = models.CharField(
        max_length=20, help_text="Wisdom Modifier", default="+0"
    )
    wisdom_save = models.CharField(
        max_length=20, help_text="Wisdom Saving Throw", default="+0"
    )

    charisma = models.CharField(max_length=50, help_text="Charisma")
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
        blank=True, null=True, help_text="Senses (e.g., darkvision 60ft)"
    )
    languages = models.TextField(blank=True, null=True, help_text="Languages known")
    gear = models.TextField(
        blank=True, null=True, help_text="Equipment, weapons, armor, and other gear"
    )
    challenge_rating = models.CharField(
        max_length=20, help_text="Challenge Rating (e.g., CR 20)"
    )

    # Actions
    traits = models.TextField(
        blank=True, null=True, help_text="Special traits and abilities"
    )
    actions = models.TextField(blank=True, null=True, help_text="Actions")
    bonus_actions = models.TextField(blank=True, null=True, help_text="Bonus Actions")
    reactions = models.TextField(blank=True, null=True, help_text="Reactions")
    legendary_actions = models.TextField(
        blank=True, null=True, help_text="Legendary Actions"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
