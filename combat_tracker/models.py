from django.db import models
from campaigns.models import Campaign
from players.models import Player
from npcs.models import NPC
from monsters.models import Monster


class CombatEncounter(models.Model):
    """Represents a combat encounter within a campaign"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='combat_encounters')
    name = models.CharField(max_length=120, help_text="Name of the encounter (e.g., 'Goblin Ambush')")
    is_active = models.BooleanField(default=False, help_text="Whether this encounter is currently active")
    current_round = models.PositiveIntegerField(default=1)
    current_turn = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.campaign.name})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('combat_tracker:encounter_detail', kwargs={'pk': self.pk})
    
    def get_participants(self):
        """Get all participants ordered by initiative (highest first)"""
        return self.participants.all().order_by('-initiative_roll')
    
    def get_living_participants(self):
        """Get only living participants ordered by initiative (highest first)"""
        return self.participants.filter(is_dead=False).order_by('-initiative_roll')
    
    def get_current_participant(self):
        """Get the participant whose turn it currently is (only living participants)"""
        living_participants = list(self.get_living_participants())
        if living_participants and self.current_turn < len(living_participants):
            return living_participants[self.current_turn]
        return None
    
    def next_turn(self):
        """Move to the next turn (skip dead participants)"""
        living_participants = list(self.get_living_participants())
        if not living_participants:
            return False
        
        self.current_turn += 1
        if self.current_turn >= len(living_participants):
            # End of round, start new round
            self.current_round += 1
            self.current_turn = 0
        self.save()
        return True
    
    def reset_encounter(self):
        """Reset the encounter to round 1, turn 0"""
        self.current_round = 1
        self.current_turn = 0
        self.is_active = False
        self.save()


class CombatParticipant(models.Model):
    """Represents a participant in a combat encounter"""
    encounter = models.ForeignKey(CombatEncounter, on_delete=models.CASCADE, related_name='participants')
    
    # Character type references
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    npc = models.ForeignKey(NPC, on_delete=models.CASCADE, null=True, blank=True)
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE, null=True, blank=True)
    
    # Custom participant (for when not using any of the above)
    name = models.CharField(max_length=120, help_text="Name of the participant")
    initiative_roll = models.PositiveIntegerField(help_text="Total initiative value")
    is_turn_complete = models.BooleanField(default=False, help_text="Whether this participant has completed their turn")
    is_dead = models.BooleanField(default=False, help_text="Whether this participant is dead (0 or negative HP)")
    
    # Combat stats (customizable during combat)
    armor_class = models.PositiveIntegerField(null=True, blank=True, help_text="Current Armor Class (can be modified by spells)")
    hit_points = models.IntegerField(null=True, blank=True, help_text="Current Hit Points (can go negative)")
    max_hit_points = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum Hit Points")
    
    # Additional combat stats for quick reference
    speed = models.CharField(max_length=50, blank=True, null=True, help_text="Movement speed")
    challenge_rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, help_text="Challenge Rating")
    
    # Ability scores for quick reference
    strength = models.PositiveIntegerField(blank=True, null=True)
    dexterity = models.PositiveIntegerField(blank=True, null=True)
    constitution = models.PositiveIntegerField(blank=True, null=True)
    intelligence = models.PositiveIntegerField(blank=True, null=True)
    wisdom = models.PositiveIntegerField(blank=True, null=True)
    charisma = models.PositiveIntegerField(blank=True, null=True)
    
    # Saving throws
    strength_save = models.IntegerField(blank=True, null=True, help_text="Strength saving throw bonus")
    dexterity_save = models.IntegerField(blank=True, null=True, help_text="Dexterity saving throw bonus")
    constitution_save = models.IntegerField(blank=True, null=True, help_text="Constitution saving throw bonus")
    intelligence_save = models.IntegerField(blank=True, null=True, help_text="Intelligence saving throw bonus")
    wisdom_save = models.IntegerField(blank=True, null=True, help_text="Wisdom saving throw bonus")
    charisma_save = models.IntegerField(blank=True, null=True, help_text="Charisma saving throw bonus")
    
    # Skills and special abilities
    skills = models.TextField(blank=True, null=True, help_text="Skills with bonuses")
    damage_resistances = models.CharField(max_length=200, blank=True, null=True, help_text="Damage resistances")
    damage_immunities = models.CharField(max_length=200, blank=True, null=True, help_text="Damage immunities")
    condition_immunities = models.CharField(max_length=200, blank=True, null=True, help_text="Condition immunities")
    senses = models.CharField(max_length=200, blank=True, null=True, help_text="Special senses")
    
    # Combat actions
    multiattack = models.TextField(blank=True, null=True, help_text="Multiattack description")
    actions = models.TextField(blank=True, null=True, help_text="Actions the creature can take")
    bonus_actions = models.TextField(blank=True, null=True, help_text="Bonus actions")
    reactions = models.TextField(blank=True, null=True, help_text="Reactions")
    legendary_actions = models.TextField(blank=True, null=True, help_text="Legendary actions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-initiative_roll']
    
    def __str__(self):
        return f"{self.get_display_name()} (Initiative: {self.initiative_roll})"
    
    @property
    def total_initiative(self):
        """Get total initiative value"""
        return self.initiative_roll
    
    def get_display_name(self):
        """Get the display name for this participant"""
        if self.player:
            return self.player.character_name
        elif self.npc:
            return self.npc.name
        elif self.monster:
            return self.monster.name
        else:
            return self.name
    
    def get_character_type_display(self):
        """Get the character type for display purposes"""
        if self.player:
            return "Player"
        elif self.npc:
            return self.npc.get_npc_type_display()
        elif self.monster:
            return f"Monster ({self.monster.get_monster_type_display()})"
        else:
            return "Custom"
    
    def get_armor_class(self):
        """Get current armor class (customizable during combat)"""
        if self.armor_class is not None:
            return self.armor_class
        elif self.player:
            return self.player.armor_class
        elif self.npc and self.npc.armor_class:
            return self.npc.armor_class
        elif self.monster:
            return self.monster.armor_class
        else:
            return 10
    
    def get_hit_points(self):
        """Get current hit points (can be negative)"""
        if self.hit_points is not None:
            return self.hit_points
        elif self.player:
            return getattr(self.player, 'hit_points', 8)
        elif self.npc and self.npc.hit_points:
            return self.npc.hit_points
        elif self.monster:
            return self.monster.hit_points
        else:
            return 8
    
    def get_max_hit_points(self):
        """Get maximum hit points"""
        if self.max_hit_points is not None:
            return self.max_hit_points
        elif self.player:
            return getattr(self.player, 'max_hit_points', 8)
        elif self.npc and self.npc.hit_points:
            return self.npc.hit_points
        elif self.monster:
            return self.monster.hit_points
        else:
            return 8
    
    def is_alive(self):
        """Check if the participant is alive (not dead)"""
        return not self.is_dead and self.get_hit_points() > 0
    
    def take_damage(self, damage):
        """Apply damage to the participant and check for death"""
        current_hp = self.get_hit_points()
        new_hp = current_hp - damage
        
        # Update hit points
        self.hit_points = new_hp
        self.save()
        
        # Check for death
        if new_hp <= 0:
            self.is_dead = True
            self.save()
            return True  # Character died
        return False  # Character survived
    
    def heal(self, healing):
        """Apply healing to the participant"""
        current_hp = self.get_hit_points()
        max_hp = self.get_max_hit_points()
        new_hp = min(max_hp, current_hp + healing)
        
        self.hit_points = new_hp
        self.save()
        
        # If healed above 0, they're no longer dead
        if new_hp > 0 and self.is_dead:
            self.is_dead = False
            self.save()
    
    def modify_armor_class(self, new_ac):
        """Modify armor class (for spells like Shield)"""
        self.armor_class = new_ac
        self.save()
    
    def get_ability_modifier(self, ability_score):
        """Calculate ability modifier from score"""
        return (ability_score - 10) // 2
    
    def get_strength_modifier(self):
        """Get strength modifier"""
        if self.strength:
            return self.get_ability_modifier(self.strength)
        return 0
    
    def get_dexterity_modifier(self):
        """Get dexterity modifier"""
        if self.dexterity:
            return self.get_ability_modifier(self.dexterity)
        return 0
    
    def get_constitution_modifier(self):
        """Get constitution modifier"""
        if self.constitution:
            return self.get_ability_modifier(self.constitution)
        return 0
    
    def get_intelligence_modifier(self):
        """Get intelligence modifier"""
        if self.intelligence:
            return self.get_ability_modifier(self.intelligence)
        return 0
    
    def get_wisdom_modifier(self):
        """Get wisdom modifier"""
        if self.wisdom:
            return self.get_ability_modifier(self.wisdom)
        return 0
    
    def get_charisma_modifier(self):
        """Get charisma modifier"""
        if self.charisma:
            return self.get_ability_modifier(self.charisma)
        return 0
    
    def populate_from_character(self):
        """Populate combat stats from the linked character"""
        if self.player:
            self.armor_class = self.player.armor_class
            self.hit_points = getattr(self.player, 'hit_points', 8)
            self.max_hit_points = getattr(self.player, 'max_hit_points', 8)
            self.speed = "30 ft."
        elif self.npc:
            self.armor_class = self.npc.armor_class
            self.hit_points = self.npc.hit_points
            self.max_hit_points = self.npc.hit_points
            self.speed = self.npc.speed
            self.challenge_rating = self.npc.challenge_rating
            self.damage_resistances = self.npc.damage_resistances
            self.condition_immunities = self.npc.condition_immunities
            self.senses = self.npc.senses
            self.actions = self.npc.actions
        elif self.monster:
            self.armor_class = self.monster.armor_class
            self.hit_points = self.monster.hit_points
            self.max_hit_points = self.monster.hit_points
            self.speed = self.monster.speed
            self.challenge_rating = self.monster.challenge_rating
            self.strength = self.monster.strength
            self.dexterity = self.monster.dexterity
            self.constitution = self.monster.constitution
            self.intelligence = self.monster.intelligence
            self.wisdom = self.monster.wisdom
            self.charisma = self.monster.charisma
            self.strength_save = self.monster.strength_save
            self.dexterity_save = self.monster.dexterity_save
            self.constitution_save = self.monster.constitution_save
            self.intelligence_save = self.monster.intelligence_save
            self.wisdom_save = self.monster.wisdom_save
            self.charisma_save = self.monster.charisma_save
            self.skills = self.monster.skills
            self.damage_resistances = self.monster.damage_resistances
            self.damage_immunities = self.monster.damage_immunities
            self.condition_immunities = self.monster.condition_immunities
            self.senses = self.monster.senses
            self.multiattack = self.monster.multiattack
            self.actions = self.monster.actions
            self.bonus_actions = self.monster.bonus_actions
            self.reactions = self.monster.reactions
            self.legendary_actions = self.monster.legendary_actions