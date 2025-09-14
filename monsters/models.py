from django.db import models


class Monster(models.Model):
    """Represents a monster or enemy creature in a campaign"""
    SIZE_CHOICES = [
        ('T', 'Tiny'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('H', 'Huge'),
        ('G', 'Gargantuan'),
    ]
    
    TYPE_CHOICES = [
        ('Aberration', 'Aberration'),
        ('Beast', 'Beast'),
        ('Celestial', 'Celestial'),
        ('Construct', 'Construct'),
        ('Dragon', 'Dragon'),
        ('Elemental', 'Elemental'),
        ('Fey', 'Fey'),
        ('Fiend', 'Fiend'),
        ('Giant', 'Giant'),
        ('Humanoid', 'Humanoid'),
        ('Monstrosity', 'Monstrosity'),
        ('Ooze', 'Ooze'),
        ('Plant', 'Plant'),
        ('Undead', 'Undead'),
        ('Swarm', 'Swarm'),
    ]
    
    name = models.CharField(max_length=120)
    monster_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='Beast')
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, default='M')
    alignment = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 'Lawful Evil', 'Chaotic Good'")
    challenge_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0.25, help_text="Challenge Rating (0.25, 0.5, 1, 2, etc.)")
    
    # Core Combat Stats
    armor_class = models.PositiveIntegerField(default=10, help_text="Armor Class")
    hit_points = models.PositiveIntegerField(default=8, help_text="Hit Points")
    speed = models.CharField(max_length=100, default='30 ft.', help_text="Movement speeds")
    
    # Ability Scores
    strength = models.PositiveIntegerField(default=10)
    dexterity = models.PositiveIntegerField(default=10)
    constitution = models.PositiveIntegerField(default=10)
    intelligence = models.PositiveIntegerField(default=10)
    wisdom = models.PositiveIntegerField(default=10)
    charisma = models.PositiveIntegerField(default=10)
    
    # Saving Throws
    strength_save = models.IntegerField(default=0, help_text="Strength saving throw bonus")
    dexterity_save = models.IntegerField(default=0, help_text="Dexterity saving throw bonus")
    constitution_save = models.IntegerField(default=0, help_text="Constitution saving throw bonus")
    intelligence_save = models.IntegerField(default=0, help_text="Intelligence saving throw bonus")
    wisdom_save = models.IntegerField(default=0, help_text="Wisdom saving throw bonus")
    charisma_save = models.IntegerField(default=0, help_text="Charisma saving throw bonus")
    
    # Skills
    skills = models.TextField(blank=True, null=True, help_text="Skills with bonuses (e.g., 'Perception +4, Stealth +6')")
    
    # Defenses
    damage_resistances = models.CharField(max_length=200, blank=True, null=True, help_text="Damage resistances")
    damage_immunities = models.CharField(max_length=200, blank=True, null=True, help_text="Damage immunities")
    condition_immunities = models.CharField(max_length=200, blank=True, null=True, help_text="Condition immunities")
    senses = models.CharField(max_length=200, blank=True, null=True, help_text="Special senses")
    languages = models.CharField(max_length=200, blank=True, null=True, help_text="Languages known")
    
    # Combat Actions
    multiattack = models.TextField(blank=True, null=True, help_text="Multiattack description")
    actions = models.TextField(blank=True, null=True, help_text="Actions the monster can take")
    bonus_actions = models.TextField(blank=True, null=True, help_text="Bonus actions")
    reactions = models.TextField(blank=True, null=True, help_text="Reactions")
    legendary_actions = models.TextField(blank=True, null=True, help_text="Legendary actions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['challenge_rating', 'name']
        verbose_name = 'Monster'
        verbose_name_plural = 'Monsters'
    
    def __str__(self):
        return f"{self.name} (CR {self.challenge_rating})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('monsters:monster_detail', kwargs={'pk': self.pk})
    
    @property
    def strength_modifier(self):
        return (self.strength - 10) // 2
    
    @property
    def dexterity_modifier(self):
        return (self.dexterity - 10) // 2
    
    @property
    def constitution_modifier(self):
        return (self.constitution - 10) // 2
    
    @property
    def intelligence_modifier(self):
        return (self.intelligence - 10) // 2
    
    @property
    def wisdom_modifier(self):
        return (self.wisdom - 10) // 2
    
    @property
    def charisma_modifier(self):
        return (self.charisma - 10) // 2
    
    @property
    def is_alive(self):
        return self.hit_points > 0
    
    @property
    def is_legendary(self):
        return bool(self.legendary_actions)
    
    @property
    def challenge_rating_display(self):
        """Display challenge rating in a readable format"""
        cr = float(self.challenge_rating)
        if cr == 0.25:
            return "1/4"
        elif cr == 0.5:
            return "1/2"
        else:
            return str(int(cr)) if cr == int(cr) else str(cr)