"""
Django Management Command for Seeding D&D Tracker Database

This command populates the database with comprehensive test data for all models
in the D&D Tracker application. It creates realistic test data including users,
campaigns, player characters, monsters, game sessions, encounters, and combat data.

⚠️  WARNING: This command DELETES ALL existing data by default!

Usage:
    python manage.py seed                    # Clear everything and seed fresh data
    python manage.py seed --no-clear         # Keep existing data (NOT recommended)
    python manage.py seed --no-factories     # Skip additional random data

Features:
- ALWAYS clears existing data before seeding (use --no-clear to skip)
- Creates diverse test data across all models
- Maintains referential integrity between related models
- Provides detailed progress output
- Handles errors gracefully with rollback capability
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import random

# Import all models
from accounts.models import User, TwoFactorCode
from campaigns.models import Campaign
from players.models import Player
from monsters.models import Monster
from game_sessions.models import Session
from combat_tracker.models import Encounter, CombatSession, CombatParticipant

# Import factories for additional random data
from dnd_tracker.factories import (
    UserFactory,
    CampaignFactory,
    PlayerFactory,
    MonsterFactory,
    SessionFactory,
    EncounterFactory,
)


class Command(BaseCommand):
    help = "Seed the database with comprehensive test data for D&D Tracker"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-clear",
            action="store_true",
            help="Skip clearing existing data before seeding (NOT recommended)",
        )
        parser.add_argument(
            "--no-factories",
            action="store_true",
            help="Skip creating additional random data using factories",
        )

    def handle(self, *args, **options):
        """Main command handler"""
        clear_data = not options.get("no_clear", False)

        self.stdout.write(
            self.style.SUCCESS("🎲 Starting D&D Tracker Database Seeding...")
        )

        try:
            with transaction.atomic():
                if clear_data:
                    self.clear_existing_data()

                # Seed data in dependency order
                self.seed_users()
                self.seed_campaigns()
                self.seed_players()
                self.seed_monsters()
                self.seed_sessions()
                self.seed_encounters()
                self.seed_combat_data()

                # Add additional random data using factories (optional)
                if not options.get("no_factories", False):
                    self.seed_additional_random_data()

                self.stdout.write(
                    self.style.SUCCESS("✅ Database seeding completed successfully!")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during seeding: {str(e)}"))
            raise

    def clear_existing_data(self):
        """Clear ALL existing data from all models"""
        self.stdout.write("🧹 Clearing ALL existing data...")

        # Clear in reverse dependency order to avoid foreign key constraints
        CombatParticipant.objects.all().delete()
        CombatSession.objects.all().delete()
        Encounter.objects.all().delete()
        Session.objects.all().delete()
        Player.objects.all().delete()
        Monster.objects.all().delete()
        Campaign.objects.all().delete()
        TwoFactorCode.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("   ✓ ALL existing data cleared")

    def seed_users(self):
        """Create test users with different configurations"""
        self.stdout.write("👥 Creating test users...")

        users_data = [
            {
                "email": "dm@example.com",
                "username": "dm_user",
                "first_name": "Alex",
                "last_name": "DungeonMaster",
                "phone_number": "+1-555-0101",
                "two_factor_enabled": False,
            },
            {
                "email": "player1@example.com",
                "username": "player1",
                "first_name": "Sarah",
                "last_name": "Wizard",
                "phone_number": "+1-555-0102",
                "two_factor_enabled": False,
            },
            {
                "email": "player2@example.com",
                "username": "player2",
                "first_name": "Mike",
                "last_name": "Fighter",
                "phone_number": "+1-555-0103",
                "two_factor_enabled": False,
            },
            {
                "email": "player3@example.com",
                "username": "player3",
                "first_name": "Emma",
                "last_name": "Rogue",
                "phone_number": "+1-555-0104",
                "two_factor_enabled": False,
            },
            {
                "email": "player4@example.com",
                "username": "player4",
                "first_name": "David",
                "last_name": "Cleric",
                "phone_number": "+1-555-0105",
                "two_factor_enabled": False,
            },
        ]

        for user_data in users_data:
            user = User.objects.create_user(password="testpass123", **user_data)
            self.stdout.write(f"   ✓ Created user: {user.email}")

        self.stdout.write("   ✓ Users created successfully")

    def seed_campaigns(self):
        """Create diverse D&D campaigns"""
        self.stdout.write("🏰 Creating campaigns...")

        campaigns_data = [
            {
                "title": "The Lost Mines of Phandelver",
                "description": """A classic D&D adventure for beginners. The party discovers 
                the lost Wave Echo Cave, a mine rich with magical ore. Along the way, they'll 
                face goblins, bandits, and ancient evils that threaten the town of Phandalin.""",
                "introduction": """Welcome to the Sword Coast! You are a group of adventurers 
                hired to escort a wagon of supplies to the frontier town of Phandalin. Little 
                do you know, this simple job will lead you to uncover ancient secrets and face 
                dangers beyond your wildest dreams.""",
                "character_requirements": """Characters should be level 1-5. All official races 
                and classes are allowed. Please create characters with motivations to help 
                others and explore the unknown.""",
            },
            {
                "title": "Curse of Strahd",
                "description": """A gothic horror adventure set in the misty realm of Barovia. 
                The party must navigate the cursed land ruled by the vampire lord Strahd von 
                Zarovich, facing werewolves, witches, and the undead while trying to escape 
                the realm's eternal darkness.""",
                "introduction": """You find yourselves lost in a thick fog, emerging in a 
                land where the sun never shines and hope seems lost. Barovia awaits, and 
                its master watches your every move from Castle Ravenloft.""",
                "character_requirements": """Characters should be level 1-10. This is a 
                horror campaign, so characters should be prepared for psychological challenges. 
                Clerics and paladins are especially useful against undead threats.""",
            },
            {
                "title": "Waterdeep: Dragon Heist",
                "description": """A treasure hunt through the City of Splendors! The party 
                becomes embroiled in a race to find a hidden vault containing half a million 
                gold dragons. Political intrigue, urban adventures, and memorable NPCs await 
                in this city-based campaign.""",
                "introduction": """Welcome to Waterdeep, the Crown of the North! In this 
                city of opportunity, anything is possible for those brave enough to seek it. 
                But beware - the city's factions have their own agendas, and gold has a way 
                of attracting dangerous attention.""",
                "character_requirements": """Characters should be level 1-5. Urban-focused 
                skills are valuable. Consider backgrounds that give you connections to 
                Waterdeep's various factions and organizations.""",
            },
            {
                "title": "Tomb of Annihilation",
                "description": """A deadly jungle adventure in Chult! The party must venture 
                into the uncharted wilderness to stop a death curse that threatens all who 
                have ever been raised from the dead. Dinosaurs, undead, and ancient traps 
                await in this challenging expedition.""",
                "introduction": """The Death Curse spreads across the world, claiming the 
                lives of those who have cheated death. Your only hope lies in the mysterious 
                jungles of Chult, where the source of this curse awaits discovery.""",
                "character_requirements": """Characters should be level 1-11. Survival skills 
                are crucial. Rangers, druids, and characters with jungle experience will be 
                particularly valuable.""",
            },
            {
                "title": "Baldur's Gate: Descent into Avernus",
                "description": """A descent into the Nine Hells! When the city of Elturel 
                disappears into Avernus, the party must venture into the first layer of Hell 
                to save the city and its people from eternal damnation.""",
                "introduction": """The city of Elturel has vanished, pulled into the depths 
                of Avernus. As heroes of Baldur's Gate, you must brave the Nine Hells to 
                save thousands of innocent souls from eternal torment.""",
                "character_requirements": """Characters should be level 1-13. This campaign 
                involves planar travel and fiendish enemies. Characters with divine magic 
                or resistance to fire will be especially useful.""",
            },
        ]

        for campaign_data in campaigns_data:
            campaign = Campaign.objects.create(**campaign_data)
            self.stdout.write(f"   ✓ Created campaign: {campaign.title}")

        self.stdout.write("   ✓ Campaigns created successfully")

    def seed_players(self):
        """Create player characters with diverse builds"""
        self.stdout.write("⚔️ Creating player characters...")

        campaigns = list(Campaign.objects.all())

        players_data = [
            {
                "character_name": "Aelindra Moonwhisper",
                "player_name": "Sarah Wizard",
                "character_class": "Wizard",
                "subclass": "School of Evocation",
                "race": "High Elf",
                "level": 5,
                "ac": 12,
                "background": """Aelindra is a scholarly elf who left her homeland to study 
                the arcane arts in Waterdeep. She's driven by curiosity and a desire to 
                understand the fundamental forces of magic. Her evocation magic focuses on 
                precise control and devastating power when needed.""",
                "campaign": campaigns[0],  # Lost Mines
            },
            {
                "character_name": "Thorin Ironbeard",
                "player_name": "Mike Fighter",
                "character_class": "Fighter",
                "subclass": "Battle Master",
                "race": "Mountain Dwarf",
                "level": 4,
                "ac": 18,
                "background": """Thorin is a veteran warrior who served in the dwarven 
                armies before becoming an adventurer. His tactical mind and combat experience 
                make him a natural leader in battle. He wields a great axe and wears heavy 
                armor with pride.""",
                "campaign": campaigns[0],  # Lost Mines
            },
            {
                "character_name": "Shadowstep",
                "player_name": "Emma Rogue",
                "character_class": "Rogue",
                "subclass": "Assassin",
                "race": "Tiefling",
                "level": 6,
                "ac": 15,
                "background": """Shadowstep is a mysterious figure who operates in the 
                shadows of Waterdeep's criminal underworld. Despite their dark reputation, 
                they have a code of honor and only targets those who truly deserve it. 
                Their infernal heritage gives them unique abilities.""",
                "campaign": campaigns[2],  # Dragon Heist
            },
            {
                "character_name": "Brother Marcus",
                "player_name": "David Cleric",
                "character_class": "Cleric",
                "subclass": "Life Domain",
                "race": "Human",
                "level": 7,
                "ac": 16,
                "background": """Brother Marcus is a devoted cleric of Lathander, the 
                Morninglord. He travels the land spreading hope and healing to those in 
                need. His divine magic is particularly effective against undead creatures, 
                making him invaluable in Barovia.""",
                "campaign": campaigns[1],  # Curse of Strahd
            },
            {
                "character_name": "Kethra Swiftwind",
                "player_name": "Alex DungeonMaster",
                "character_class": "Ranger",
                "subclass": "Beast Master",
                "race": "Wood Elf",
                "level": 8,
                "ac": 14,
                "background": """Kethra is a skilled tracker and survivalist who has spent 
                years exploring the jungles of Chult. Her animal companion, a panther named 
                Shadowfang, is her closest ally. She's determined to stop the Death Curse 
                and save those affected by it.""",
                "campaign": campaigns[3],  # Tomb of Annihilation
            },
            {
                "character_name": "Zariel's Bane",
                "player_name": "Mike Fighter",
                "character_class": "Paladin",
                "subclass": "Oath of Vengeance",
                "race": "Aasimar",
                "level": 9,
                "ac": 19,
                "background": """This paladin has sworn an oath of vengeance against the 
                forces of evil, particularly the archdevil Zariel. Their celestial heritage 
                gives them power over fiends, and they're determined to save Elturel from 
                its fate in Avernus.""",
                "campaign": campaigns[4],  # Descent into Avernus
            },
            {
                "character_name": "Grimjaw",
                "player_name": "Emma Rogue",
                "character_class": "Barbarian",
                "subclass": "Path of the Totem Warrior",
                "race": "Half-Orc",
                "level": 3,
                "ac": 13,
                "background": """Grimjaw is a fierce warrior who channels the spirit of 
                the bear through his totem magic. Despite his intimidating appearance, he 
                has a strong sense of honor and protects those weaker than himself. His 
                rage is legendary among his allies.""",
                "campaign": campaigns[0],  # Lost Mines
            },
            {
                "character_name": "Luna Starweaver",
                "player_name": "Sarah Wizard",
                "character_class": "Sorcerer",
                "subclass": "Wild Magic",
                "race": "Gnome",
                "level": 4,
                "ac": 11,
                "background": """Luna is a chaotic gnome whose wild magic surges create 
                unpredictable effects. She's cheerful and optimistic, always ready to 
                help her friends despite the occasional magical mishap. Her spells can 
                be powerful but unpredictable.""",
                "campaign": campaigns[2],  # Dragon Heist
            },
        ]

        for player_data in players_data:
            player = Player.objects.create(**player_data)
            self.stdout.write(f"   ✓ Created player: {player.character_name}")

        self.stdout.write("   ✓ Player characters created successfully")

    def seed_monsters(self):
        """Create monsters with complete statistics"""
        self.stdout.write("🐉 Creating monsters...")

        monsters_data = [
            {
                "name": "Goblin",
                "ac": 15,
                "initiative": "+2",
                "hp": "7 (2d6)",
                "speed": "30 ft",
                "strength": "8 (-1)",
                "strength_mod": "-1",
                "strength_save": "-1",
                "dexterity": "14 (+2)",
                "dexterity_mod": "+2",
                "dexterity_save": "+2",
                "constitution": "10 (+0)",
                "constitution_mod": "+0",
                "constitution_save": "+0",
                "intelligence": "10 (+0)",
                "intelligence_mod": "+0",
                "intelligence_save": "+0",
                "wisdom": "8 (-1)",
                "wisdom_mod": "-1",
                "wisdom_save": "-1",
                "charisma": "8 (-1)",
                "charisma_mod": "-1",
                "charisma_save": "-1",
                "skills": "Stealth +6",
                "senses": "Darkvision 60 ft",
                "languages": "Common, Goblin",
                "challenge_rating": "CR 1/4",
                "traits": """Nimble Escape. The goblin can take the Disengage or Hide action 
                as a bonus action on each of its turns.""",
                "actions": """Scimitar. Melee Weapon Attack: +4 to hit, reach 5 ft, one target. 
                Hit: 5 (1d6 + 2) slashing damage.\n\nShortbow. Ranged Weapon Attack: +4 to hit, 
                range 80/320 ft, one target. Hit: 5 (1d6 + 2) piercing damage.""",
            },
            {
                "name": "Orc",
                "ac": 13,
                "initiative": "+1",
                "hp": "15 (2d8 + 6)",
                "speed": "30 ft",
                "strength": "16 (+3)",
                "strength_mod": "+3",
                "strength_save": "+3",
                "dexterity": "12 (+1)",
                "dexterity_mod": "+1",
                "dexterity_save": "+1",
                "constitution": "16 (+3)",
                "constitution_mod": "+3",
                "constitution_save": "+3",
                "intelligence": "7 (-2)",
                "intelligence_mod": "-2",
                "intelligence_save": "-2",
                "wisdom": "11 (+0)",
                "wisdom_mod": "+0",
                "wisdom_save": "+0",
                "charisma": "10 (+0)",
                "charisma_mod": "+0",
                "charisma_save": "+0",
                "senses": "Darkvision 60 ft",
                "languages": "Common, Orc",
                "challenge_rating": "CR 1/2",
                "traits": """Aggressive. As a bonus action, the orc can move up to its speed 
                toward a hostile creature that it can see.""",
                "actions": """Greataxe. Melee Weapon Attack: +5 to hit, reach 5 ft, one target. 
                Hit: 9 (1d12 + 3) slashing damage.\n\nJavelin. Melee or Ranged Weapon Attack: 
                +5 to hit, reach 5 ft or range 30/120 ft, one target. Hit: 6 (1d6 + 3) 
                piercing damage.""",
            },
            {
                "name": "Strahd von Zarovich",
                "ac": 16,
                "initiative": "+7",
                "hp": "144 (17d8 + 68)",
                "speed": "30 ft, climb 30 ft",
                "strength": "18 (+4)",
                "strength_mod": "+4",
                "strength_save": "+9",
                "dexterity": "18 (+4)",
                "dexterity_mod": "+4",
                "dexterity_save": "+9",
                "constitution": "18 (+4)",
                "constitution_mod": "+4",
                "constitution_save": "+9",
                "intelligence": "20 (+5)",
                "intelligence_mod": "+5",
                "intelligence_save": "+10",
                "wisdom": "15 (+2)",
                "wisdom_mod": "+2",
                "wisdom_save": "+7",
                "charisma": "18 (+4)",
                "charisma_mod": "+4",
                "charisma_save": "+9",
                "skills": "Deception +9, Insight +7, Intimidation +9, Perception +7",
                "resistances": "Necrotic; Bludgeoning, Piercing, and Slashing from Nonmagical Attacks",
                "immunities": "Charmed, Exhaustion, Frightened, Poisoned",
                "senses": "Darkvision 120 ft",
                "languages": "Common, Draconic, Elvish, Giant",
                "challenge_rating": "CR 15",
                "traits": """Legendary Resistance (3/Day). If Strahd fails a saving throw, 
                he can choose to succeed instead.\n\nSpider Climb. Strahd can climb difficult 
                surfaces, including upside down on ceilings, without needing to make an 
                ability check.\n\nVampire Weaknesses. Strahd has the following flaws:\n• 
                Forbiddance. Strahd can't enter a residence without an invitation from one 
                of the occupants.\n• Harmed by Running Water. Strahd takes 20 acid damage 
                if he ends his turn in running water.\n• Stake to the Heart. If a piercing 
                weapon made of wood is driven into Strahd's heart while he is incapacitated 
                in his resting place, he is paralyzed until the stake is removed.\n• Sunlight 
                Hypersensitivity. Strahd takes 20 radiant damage when he starts his turn 
                in sunlight. While in sunlight, he has disadvantage on attack rolls and 
                ability checks.""",
                "actions": """Unarmed Strike. Melee Weapon Attack: +9 to hit, reach 5 ft, 
                one target. Hit: 8 (1d8 + 4) bludgeoning damage plus 10 (3d6) necrotic damage.\n\n 
                Charm. Strahd targets one humanoid he can see within 30 feet of him. If the 
                target can see Strahd, the target must succeed on a DC 17 Wisdom saving throw 
                against this magic or be charmed by Strahd.\n\nChildren of the Night (1/Day). 
                Strahd magically calls 2d4 swarms of bats or swarms of rats, provided that 
                the sun isn't up. While outdoors, Strahd can choose to call 3d6 wolves instead. 
                The called creatures arrive in 1d4 rounds, acting as allies of Strahd and 
                obeying his spoken commands.""",
                "legendary_actions": """Move. Strahd moves up to his speed without provoking 
                opportunity attacks.\n\nUnarmed Strike. Strahd makes one unarmed strike.\n\n 
                Charm (Costs 2 Actions). Strahd uses his Charm action.""",
            },
            {
                "name": "Ancient Red Dragon",
                "ac": 22,
                "initiative": "+0",
                "hp": "546 (28d20 + 252)",
                "speed": "40 ft, climb 40 ft, fly 80 ft",
                "strength": "30 (+10)",
                "strength_mod": "+10",
                "strength_save": "+17",
                "dexterity": "10 (+0)",
                "dexterity_mod": "+0",
                "dexterity_save": "+7",
                "constitution": "29 (+9)",
                "constitution_mod": "+9",
                "constitution_save": "+16",
                "intelligence": "18 (+4)",
                "intelligence_mod": "+4",
                "intelligence_save": "+11",
                "wisdom": "15 (+2)",
                "wisdom_mod": "+2",
                "wisdom_save": "+9",
                "charisma": "23 (+6)",
                "charisma_mod": "+6",
                "charisma_save": "+13",
                "skills": "Perception +16, Stealth +7",
                "immunities": "Fire",
                "senses": "Blindsight 60 ft, Darkvision 120 ft",
                "languages": "Common, Draconic",
                "challenge_rating": "CR 24",
                "traits": """Legendary Resistance (3/Day). If the dragon fails a saving throw, 
                it can choose to succeed instead.\n\nMagic Resistance. The dragon has advantage 
                on saving throws against spells and other magical effects.\n\nSiege Monster. 
                The dragon deals double damage to objects and structures.""",
                "actions": """Multiattack. The dragon can use its Frightful Presence. It then 
                makes three attacks: one with its bite and two with its claws.\n\nBite. Melee 
                Weapon Attack: +17 to hit, reach 15 ft, one target. Hit: 21 (2d10 + 10) 
                piercing damage plus 14 (4d6) fire damage.\n\nClaw. Melee Weapon Attack: +17 
                to hit, reach 10 ft, one target. Hit: 17 (2d6 + 10) slashing damage.\n\nTail. 
                Melee Weapon Attack: +17 to hit, reach 20 ft, one target. Hit: 19 (2d8 + 10) 
                bludgeoning damage.\n\nFrightful Presence. Each creature of the dragon's choice 
                that is within 120 feet of the dragon and aware of it must succeed on a DC 21 
                Wisdom saving throw or become frightened for 1 minute.\n\nFire Breath (Recharge 
                5-6). The dragon exhales fire in a 90-foot cone. Each creature in that area 
                must make a DC 24 Dexterity saving throw, taking 91 (26d6) fire damage on a 
                failed save, or half as much damage on a successful one.""",
                "legendary_actions": """Detect. The dragon makes a Wisdom (Perception) check.\n\n 
                Tail Attack. The dragon makes a tail attack.\n\nWing Attack (Costs 2 Actions). 
                The dragon beats its wings. Each creature within 15 feet of the dragon must 
                succeed on a DC 25 Dexterity saving throw or take 17 (2d6 + 10) bludgeoning 
                damage and be knocked prone.""",
            },
            {
                "name": "Beholder",
                "ac": 18,
                "initiative": "+1",
                "hp": "180 (19d10 + 76)",
                "speed": "0 ft, fly 20 ft (hover)",
                "strength": "10 (+0)",
                "strength_mod": "+0",
                "strength_save": "+0",
                "dexterity": "14 (+2)",
                "dexterity_mod": "+2",
                "dexterity_save": "+2",
                "constitution": "18 (+4)",
                "constitution_mod": "+4",
                "constitution_save": "+4",
                "intelligence": "17 (+3)",
                "intelligence_mod": "+3",
                "intelligence_save": "+3",
                "wisdom": "15 (+2)",
                "wisdom_mod": "+2",
                "wisdom_save": "+2",
                "charisma": "17 (+3)",
                "charisma_mod": "+3",
                "charisma_save": "+3",
                "skills": "Perception +12",
                "senses": "Darkvision 120 ft",
                "languages": "Deep Speech, Undercommon",
                "challenge_rating": "CR 13",
                "traits": """Antimagic Cone. The beholder's central eye creates an area of 
                antimagic, as in the antimagic field spell, in a 150-foot cone. At the start 
                of each of its turns, the beholder decides which way the cone faces and whether 
                the cone is active.\n\nLegendary Resistance (3/Day). If the beholder fails a 
                saving throw, it can choose to succeed instead.""",
                "actions": """Bite. Melee Weapon Attack: +5 to hit, reach 5 ft, one target. 
                Hit: 14 (4d6) piercing damage.\n\nEye Rays. The beholder shoots three of the 
                following magical eye rays at random (reroll duplicates), choosing one to three 
                targets it can see within 120 feet of it:\n\n1. Charm Ray. The targeted creature 
                must succeed on a DC 16 Wisdom saving throw or be charmed by the beholder for 
                1 hour, or until the beholder harms the creature.\n\n2. Paralyzing Ray. The 
                targeted creature must succeed on a DC 16 Constitution saving throw or be 
                paralyzed for 1 minute. The target can repeat the saving throw at the end of 
                each of its turns, ending the effect on itself on a success.\n\n3. Fear Ray. 
                The targeted creature must succeed on a DC 16 Wisdom saving throw or be 
                frightened for 1 minute. The target can repeat the saving throw at the end 
                of each of its turns, ending the effect on itself on a success.\n\n4. Slowing 
                Ray. The targeted creature must succeed on a DC 16 Dexterity saving throw. On 
                a failed save, the target's speed is halved for 1 minute. In addition, the 
                creature can't take reactions, and it can take either an action or a bonus 
                action on its turn, not both. The creature can repeat the saving throw at 
                the end of each of its turns, ending the effect on itself on a success.\n\n5. 
                Enervation Ray. The targeted creature must make a DC 16 Constitution saving 
                throw, taking 36 (8d8) necrotic damage on a failed save, or half as much 
                damage on a successful one.\n\n6. Telekinetic Ray. The targeted creature must 
                succeed on a DC 16 Strength saving throw or be moved up to 30 feet in any 
                direction. It is restrained by the ray's telekinetic grip until the end of 
                the beholder's next turn or until the beholder is incapacitated.\n\n7. Sleep 
                Ray. The targeted creature must succeed on a DC 16 Wisdom saving throw or fall 
                asleep and remain unconscious for 1 minute. The target awakens if it takes 
                damage or if someone uses an action to shake or slap it awake.\n\n8. Petrification 
                Ray. The targeted creature must make a DC 16 Dexterity saving throw. On a 
                failed save, the creature begins to turn to stone and is restrained. It must 
                repeat the saving throw at the end of its next turn. On a success, the effect 
                ends. On a failure, the creature is petrified until freed by the greater 
                restoration spell or other magic.\n\n9. Disintegration Ray. If the target is 
                a creature, it must succeed on a DC 16 Dexterity saving throw or take 45 (10d8) 
                force damage. If this damage reduces the target to 0 hit points, its body becomes 
                a pile of fine gray dust.\n\n10. Death Ray. The targeted creature must succeed 
                on a DC 16 Dexterity saving throw or take 55 (10d10) necrotic damage. The 
                target dies if the ray reduces it to 0 hit points.""",
                "legendary_actions": """Eye Ray. The beholder uses one random eye ray.""",
            },
        ]

        for monster_data in monsters_data:
            monster = Monster.objects.create(**monster_data)
            self.stdout.write(f"   ✓ Created monster: {monster.name}")

        self.stdout.write("   ✓ Monsters created successfully")

    def seed_sessions(self):
        """Create game sessions with planning and session notes"""
        self.stdout.write("📝 Creating game sessions...")

        campaigns = list(Campaign.objects.all())

        sessions_data = [
            {
                "campaign": campaigns[0],  # Lost Mines
                "planning_notes": """Session 1: Goblin Ambush
                - Start with the wagon escort mission
                - Goblin ambush on the Triboar Trail
                - Lead to Cragmaw Hideout
                - Introduce Sildar Hallwinter
                - End with arrival in Phandalin""",
                "session_notes": """The party successfully defended the wagon from goblin 
                attackers. Aelindra's fireball was particularly effective. Thorin took 
                some damage but fought bravely. The party discovered clues about the 
                Cragmaw goblins and decided to investigate their hideout.""",
                "session_date": date.today() - timedelta(days=7),
            },
            {
                "campaign": campaigns[0],  # Lost Mines
                "planning_notes": """Session 2: Cragmaw Hideout
                - Explore the goblin cave
                - Rescue Sildar Hallwinter
                - Learn about the Black Spider
                - Discover map to Wave Echo Cave
                - Return to Phandalin""",
                "session_notes": """The party successfully infiltrated the Cragmaw Hideout. 
                Shadowstep's stealth skills were invaluable. They rescued Sildar and learned 
                about the Black Spider's plans. The map to Wave Echo Cave was recovered, 
                setting up the next phase of the adventure.""",
                "session_date": date.today() - timedelta(days=14),
            },
            {
                "campaign": campaigns[1],  # Curse of Strahd
                "planning_notes": """Session 1: Death House
                - Party arrives in Barovia
                - Explore the Death House
                - Face the cultists and shadows
                - Confront the shambling mound
                - Gain levels and equipment""",
                "session_notes": """The party entered the cursed Death House and faced 
                numerous horrors. Brother Marcus's divine magic was crucial against the 
                undead. The shambling mound nearly killed several party members, but they 
                prevailed through teamwork and determination.""",
                "session_date": date.today() - timedelta(days=21),
            },
            {
                "campaign": campaigns[2],  # Dragon Heist
                "planning_notes": """Session 1: Trollskull Manor
                - Party receives the deed to Trollskull Manor
                - Explore the haunted tavern
                - Meet the neighbors
                - Begin faction introductions
                - Plan tavern renovation""",
                "session_notes": """The party was thrilled to receive their own tavern! 
                Luna's wild magic caused some amusing mishaps during exploration. The party 
                met several interesting NPCs and began making plans to renovate the manor. 
                The mystery of the missing gold dragons deepens.""",
                "session_date": date.today() - timedelta(days=28),
            },
            {
                "campaign": campaigns[3],  # Tomb of Annihilation
                "planning_notes": """Session 1: Port Nyanzaru
                - Arrive in Chult
                - Meet Syndra Silvane
                - Explore the city
                - Hire guides
                - Prepare for jungle expedition""",
                "session_notes": """The party arrived in the exotic city of Port Nyanzaru. 
                Kethra's knowledge of Chult proved invaluable. They hired a guide named 
                Salida and began preparing for their dangerous journey into the jungle. 
                The Death Curse's effects are becoming more apparent.""",
                "session_date": date.today() - timedelta(days=35),
            },
        ]

        for session_data in sessions_data:
            session = Session.objects.create(**session_data)
            self.stdout.write(
                f"   ✓ Created session: {session.campaign.title} - {session.session_date}"
            )

        self.stdout.write("   ✓ Game sessions created successfully")

    def seed_encounters(self):
        """Create combat encounters with players and monsters"""
        self.stdout.write("⚔️ Creating encounters...")

        campaigns = list(Campaign.objects.all())
        players = list(Player.objects.all())
        monsters = list(Monster.objects.all())

        encounters_data = [
            {
                "name": "Goblin Ambush",
                "description": """A group of goblins has set up an ambush along the Triboar 
                Trail, hoping to rob travelers of their valuables. The goblins are hidden 
                in the trees and bushes, ready to strike when the party passes by.""",
                "campaign": campaigns[0],  # Lost Mines
                "players": [
                    players[0],
                    players[1],
                    players[6],
                ],  # Aelindra, Thorin, Grimjaw
                "monsters": [monsters[0], monsters[0], monsters[0]],  # 3 Goblins
            },
            {
                "name": "Cragmaw Hideout",
                "description": """The party must infiltrate the goblin hideout to rescue 
                Sildar Hallwinter. The cave is filled with traps, goblins, and their 
                worg companion. Stealth and strategy will be key to success.""",
                "campaign": campaigns[0],  # Lost Mines
                "players": [
                    players[0],
                    players[1],
                    players[6],
                ],  # Aelindra, Thorin, Grimjaw
                "monsters": [
                    monsters[0],
                    monsters[0],
                    monsters[0],
                    monsters[1],
                ],  # 3 Goblins, 1 Orc
            },
            {
                "name": "Strahd's Dinner Invitation",
                "description": """The party has been invited to dinner at Castle Ravenloft. 
                Strahd von Zarovich himself will be their host, and the encounter could 
                turn deadly at any moment. Diplomacy and courage will be tested.""",
                "campaign": campaigns[1],  # Curse of Strahd
                "players": [players[3]],  # Brother Marcus
                "monsters": [monsters[2]],  # Strahd
            },
            {
                "name": "Xanathar's Lair",
                "description": """The party must infiltrate the Xanathar Guild's lair to 
                recover the stolen gold dragons. The beholder Xanathar guards his treasure 
                fiercely, and the party will need all their wits and courage to survive.""",
                "campaign": campaigns[2],  # Dragon Heist
                "players": [players[2], players[7]],  # Shadowstep, Luna
                "monsters": [monsters[4]],  # Beholder
            },
            {
                "name": "Jungle Temple Guardians",
                "description": """Deep in the Chultan jungle, the party discovers an ancient 
                temple guarded by powerful creatures. They must defeat the guardians to 
                access the temple's secrets and continue their quest to stop the Death Curse.""",
                "campaign": campaigns[3],  # Tomb of Annihilation
                "players": [players[4]],  # Kethra
                "monsters": [monsters[3]],  # Ancient Red Dragon
            },
            {
                "name": "Avernus Battle",
                "description": """In the depths of Avernus, the party faces off against 
                the forces of Zariel. This epic battle will determine the fate of Elturel 
                and thousands of innocent souls. Only the bravest heroes can prevail.""",
                "campaign": campaigns[4],  # Descent into Avernus
                "players": [players[5]],  # Zariel's Bane
                "monsters": [monsters[3], monsters[1]],  # Ancient Red Dragon, Orc
            },
        ]

        for encounter_data in encounters_data:
            encounter = Encounter.objects.create(
                name=encounter_data["name"],
                description=encounter_data["description"],
                campaign=encounter_data["campaign"],
            )

            # Add players and monsters
            encounter.players.set(encounter_data["players"])
            encounter.monsters.set(encounter_data["monsters"])

            self.stdout.write(f"   ✓ Created encounter: {encounter.name}")

        self.stdout.write("   ✓ Encounters created successfully")

    def seed_combat_data(self):
        """Create active combat sessions and participants"""
        self.stdout.write("🎲 Creating combat sessions...")

        encounters = list(Encounter.objects.all())

        # Create a few active combat sessions
        for i, encounter in enumerate(encounters[:3]):  # First 3 encounters
            combat_session = CombatSession.objects.create(
                encounter=encounter,
                current_round=random.randint(1, 3),
                current_turn_index=random.randint(0, 2),
                is_active=True,
            )

            # Create participants for this combat session
            participants = []

            # Add player participants
            for player in encounter.players.all():
                participant = CombatParticipant.objects.create(
                    combat_session=combat_session,
                    participant_type="player",
                    player=player,
                    initiative=random.randint(1, 20),
                    current_hp=random.randint(
                        1, player.level * 8
                    ),  # Rough HP calculation
                    max_hp=player.level * 8,
                    is_dead=False,
                    turn_completed=False,
                )
                participants.append(participant)

            # Add monster participants
            for monster in encounter.monsters.all():
                # Extract HP from monster's hp field (simplified)
                max_hp = 50 if "d20" in monster.hp else 20  # Rough estimation

                participant = CombatParticipant.objects.create(
                    combat_session=combat_session,
                    participant_type="monster",
                    monster=monster,
                    initiative=random.randint(1, 20),
                    current_hp=random.randint(1, max_hp),
                    max_hp=max_hp,
                    is_dead=False,
                    turn_completed=False,
                )
                participants.append(participant)

            # Sort participants by initiative (highest first)
            participants.sort(key=lambda p: p.initiative, reverse=True)

            # Update turn index to point to the first participant
            combat_session.current_turn_index = 0
            combat_session.save()

            self.stdout.write(
                f"   ✓ Created combat session: {combat_session.encounter.name} (Round {combat_session.current_round})"
            )

        self.stdout.write("   ✓ Combat sessions created successfully")

    def seed_additional_random_data(self):
        """Create additional random data using factories for more comprehensive testing"""
        self.stdout.write("🎲 Creating additional random data...")

        # Create additional random users
        additional_users = UserFactory.create_batch(3)
        self.stdout.write(f"   ✓ Created {len(additional_users)} additional users")

        # Create additional random campaigns
        additional_campaigns = CampaignFactory.create_batch(2)
        self.stdout.write(
            f"   ✓ Created {len(additional_campaigns)} additional campaigns"
        )

        # Create additional random players for the new campaigns
        for campaign in additional_campaigns:
            players = PlayerFactory.create_batch(3, campaign=campaign)
            self.stdout.write(f"   ✓ Created 3 players for campaign: {campaign.title}")

        # Create additional random monsters
        additional_monsters = MonsterFactory.create_batch(5)
        self.stdout.write(
            f"   ✓ Created {len(additional_monsters)} additional monsters"
        )

        # Create additional random sessions
        all_campaigns = list(Campaign.objects.all())
        for campaign in all_campaigns[-2:]:  # Last 2 campaigns (the random ones)
            sessions = SessionFactory.create_batch(2, campaign=campaign)
            self.stdout.write(f"   ✓ Created 2 sessions for campaign: {campaign.title}")

        # Create additional random encounters
        additional_encounters = EncounterFactory.create_batch(3)
        self.stdout.write(
            f"   ✓ Created {len(additional_encounters)} additional encounters"
        )

        self.stdout.write("   ✓ Additional random data created successfully")
