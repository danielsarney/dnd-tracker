from django.db import models


class NPC(models.Model):
    """Represents a Non-Player Character in a campaign"""
    SIZE_CHOICES = [
        ('T', 'Tiny'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('H', 'Huge'),
        ('G', 'Gargantuan'),
    ]
    
    name = models.CharField(max_length=120)
    race = models.CharField(max_length=80, blank=True, null=True, help_text="Race (Human, Elf, Dwarf, etc.)")
    occupation = models.CharField(max_length=80, blank=True, null=True, help_text="Occupation (Blacksmith, Merchant, Guard, etc.)")
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, default='M', help_text="Creature size")
    location = models.CharField(max_length=200, blank=True, null=True, help_text="Where this NPC can be found")
    background = models.TextField(blank=True, null=True, help_text="Their history and role in the world")
    
    # Core Combat Stats
    armor_class = models.PositiveIntegerField(blank=True, null=True, help_text="Armor Class")
    hit_points = models.PositiveIntegerField(blank=True, null=True, help_text="Hit Points")
    level = models.PositiveIntegerField(blank=True, null=True, help_text="Character Level")
    speed = models.CharField(max_length=100, blank=True, null=True, help_text="Movement speeds")
    
    # Ability Scores
    strength = models.PositiveIntegerField(default=10, help_text="Strength score")
    dexterity = models.PositiveIntegerField(default=10, help_text="Dexterity score")
    constitution = models.PositiveIntegerField(default=10, help_text="Constitution score")
    intelligence = models.PositiveIntegerField(default=10, help_text="Intelligence score")
    wisdom = models.PositiveIntegerField(default=10, help_text="Wisdom score")
    charisma = models.PositiveIntegerField(default=10, help_text="Charisma score")
    
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
    actions = models.TextField(blank=True, null=True, help_text="Actions the NPC can take")
    bonus_actions = models.TextField(blank=True, null=True, help_text="Bonus actions")
    reactions = models.TextField(blank=True, null=True, help_text="Reactions")
    legendary_actions = models.TextField(blank=True, null=True, help_text="Legendary actions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['level', 'name']
        verbose_name = 'NPC'
        verbose_name_plural = 'NPCs'
    
    def __str__(self):
        return f"{self.name}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('npcs:npc_detail', kwargs={'pk': self.pk})
    
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
    def is_combat_ready(self):
        """Check if NPC has essential combat stats"""
        return self.armor_class is not None and self.hit_points is not None
    
    @property
    def is_alive(self):
        return self.hit_points > 0 if self.hit_points else False
    
    @property
    def is_legendary(self):
        return bool(self.legendary_actions)
    
    @property
    def level_display(self):
        """Display level in a readable format"""
        if not self.level:
            return None
        return str(self.level)