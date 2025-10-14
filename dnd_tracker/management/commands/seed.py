from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
import random

from accounts.models import TwoFactorCode
from campaigns.models import Campaign
from players.models import Player
from monsters.models import Monster
from game_sessions.models import Session
from combat_tracker.models import Encounter

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding (default: True)',
        )
        parser.add_argument(
            '--no-clear',
            action='store_true',
            help='Skip clearing existing data',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of users to create (default: 5)',
        )
        parser.add_argument(
            '--campaigns',
            type=int,
            default=3,
            help='Number of campaigns to create (default: 3)',
        )
        parser.add_argument(
            '--monsters',
            type=int,
            default=10,
            help='Number of monsters to create (default: 10)',
        )

    def handle(self, *args, **options):
        clear_data = options['clear'] or not options['no_clear']
        
        if clear_data:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        self.stdout.write('Seeding database with test data...')
        
        with transaction.atomic():
            # Create users
            users = self.create_users(options['users'])
            
            # Create campaigns
            campaigns = self.create_campaigns(options['campaigns'])
            
            # Create players for each campaign
            players = self.create_players(campaigns)
            
            # Create monsters
            monsters = self.create_monsters(options['monsters'])
            
            # Create game sessions
            sessions = self.create_sessions(campaigns)
            
            # Create encounters
            encounters = self.create_encounters(campaigns, players, monsters)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'- {len(users)} users\n'
                f'- {len(campaigns)} campaigns\n'
                f'- {len(players)} players\n'
                f'- {len(monsters)} monsters\n'
                f'- {len(sessions)} game sessions\n'
                f'- {len(encounters)} encounters'
            )
        )

    def clear_data(self):
        """Clear all existing data"""
        Encounter.objects.all().delete()
        Session.objects.all().delete()
        Monster.objects.all().delete()
        Player.objects.all().delete()
        Campaign.objects.all().delete()
        TwoFactorCode.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()  # Keep superusers

    def create_users(self, count):
        """Create test users"""
        users = []
        for i in range(count):
            user = User.objects.create_user(
                username=f'testuser{i+1}',
                email=f'testuser{i+1}@example.com',
                first_name=f'Test{i+1}',
                last_name='User',
                password='testpass123',
                phone_number=f'+123456789{i:02d}',
                is_active=True
            )
            users.append(user)
        
        # Create one superuser
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        users.append(superuser)
        
        return users

    def create_campaigns(self, count):
        """Create test campaigns"""
        campaigns_data = [
            {
                'title': 'The Lost Mines of Phandelver',
                'description': 'A classic D&D adventure for new players, featuring goblins, dragons, and ancient magic.',
                'introduction': 'You are hired to escort a wagon of supplies to the frontier town of Phandalin. But when you arrive, you discover the town is in trouble...',
                'character_requirements': 'Level 1-5 characters. Any race or class welcome. New players encouraged.'
            },
            {
                'title': 'Curse of Strahd',
                'description': 'A gothic horror adventure in the cursed land of Barovia, ruled by the vampire lord Strahd von Zarovich.',
                'introduction': 'You find yourselves trapped in the misty realm of Barovia, where the vampire Strahd rules with an iron fist...',
                'character_requirements': 'Level 1-10 characters. Gothic horror themes. Not recommended for new players.'
            },
            {
                'title': 'Waterdeep: Dragon Heist',
                'description': 'A treasure hunt through the City of Splendors, featuring political intrigue and urban adventure.',
                'introduction': 'In the bustling city of Waterdeep, rumors spread of a vast treasure hidden somewhere in the city...',
                'character_requirements': 'Level 1-5 characters. Urban adventure with political elements.'
            },
            {
                'title': 'Tomb of Annihilation',
                'description': 'A deadly jungle adventure featuring dinosaurs, undead, and the infamous Tomb of Horrors.',
                'introduction': 'The death curse spreads across Faerûn, and only brave adventurers can stop it by venturing into the jungles of Chult...',
                'character_requirements': 'Level 1-11 characters. High difficulty, experienced players recommended.'
            },
            {
                'title': 'Baldur\'s Gate: Descent into Avernus',
                'description': 'A descent into the Nine Hells to save the city of Elturel from eternal damnation.',
                'introduction': 'The city of Elturel has vanished, pulled into Avernus, the first layer of the Nine Hells...',
                'character_requirements': 'Level 1-13 characters. Infernal themes and high stakes.'
            }
        ]
        
        campaigns = []
        for i in range(min(count, len(campaigns_data))):
            campaign = Campaign.objects.create(**campaigns_data[i])
            campaigns.append(campaign)
        
        return campaigns

    def create_players(self, campaigns):
        """Create test players for campaigns"""
        players = []
        
        # Character classes and races
        classes = ['Fighter', 'Wizard', 'Rogue', 'Cleric', 'Ranger', 'Paladin', 'Barbarian', 'Bard', 'Druid', 'Monk', 'Sorcerer', 'Warlock']
        subclasses = ['Champion', 'Eldritch Knight', 'Battle Master', 'Evocation', 'Abjuration', 'Divination', 'Thief', 'Assassin', 'Arcane Trickster', 'Life', 'Light', 'War', 'Beast Master', 'Hunter', 'Devotion', 'Ancients', 'Berserker', 'Totem Warrior', 'Lore', 'Valor', 'Moon', 'Land', 'Open Hand', 'Shadow', 'Draconic', 'Wild Magic', 'Fiend', 'Great Old One']
        races = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling', 'Aasimar', 'Genasi', 'Goliath']
        
        backgrounds = [
            'Acolyte - Former temple servant with knowledge of religious practices',
            'Criminal - Former thief with connections to the underworld',
            'Folk Hero - Local legend who stood up against tyranny',
            'Noble - Scion of a wealthy family with political connections',
            'Sage - Scholar with vast knowledge of history and lore',
            'Soldier - Former military with combat training and discipline',
            'Charlatan - Confidence trickster with false identities',
            'Entertainer - Performer with skills in music and acting',
            'Guild Artisan - Skilled craftsman with guild connections',
            'Hermit - Reclusive scholar with secret knowledge',
            'Knight - Noble warrior with a code of honor',
            'Outlander - Wilderness survivor with tracking skills',
            'Sailor - Former seafarer with nautical knowledge',
            'Spy - Covert operative with infiltration skills'
        ]
        
        for campaign in campaigns:
            # Create 3-5 players per campaign
            num_players = random.randint(3, 5)
            for i in range(num_players):
                player = Player.objects.create(
                    character_name=f'{random.choice(races)} {random.choice(classes)} {i+1}',
                    player_name=f'Player {i+1}',
                    character_class=random.choice(classes),
                    subclass=random.choice(subclasses) if random.random() > 0.3 else '',
                    race=random.choice(races),
                    level=random.randint(1, 8),
                    ac=random.randint(12, 18),
                    background=random.choice(backgrounds),
                    campaign=campaign
                )
                players.append(player)
        
        return players

    def create_monsters(self, count):
        """Create test monsters"""
        monsters_data = [
            {
                'name': 'Goblin',
                'ac': 15,
                'initiative': '+2',
                'hp': '7 (2d6)',
                'speed': '30 ft.',
                'strength': '8 (-1)',
                'strength_mod': '-1',
                'strength_save': '-1',
                'dexterity': '14 (+2)',
                'dexterity_mod': '+2',
                'dexterity_save': '+2',
                'constitution': '10 (+0)',
                'constitution_mod': '+0',
                'constitution_save': '+0',
                'intelligence': '10 (+0)',
                'intelligence_mod': '+0',
                'intelligence_save': '+0',
                'wisdom': '8 (-1)',
                'wisdom_mod': '-1',
                'wisdom_save': '-1',
                'charisma': '8 (-1)',
                'charisma_mod': '-1',
                'charisma_save': '-1',
                'skills': 'Stealth +6',
                'senses': 'Darkvision 60 ft.',
                'languages': 'Common, Goblin',
                'challenge_rating': 'CR 1/4',
                'actions': 'Scimitar. Melee Weapon Attack: +4 to hit, reach 5 ft., one target. Hit: 5 (1d6 + 2) slashing damage.'
            },
            {
                'name': 'Orc',
                'ac': 13,
                'initiative': '+1',
                'hp': '15 (2d8 + 6)',
                'speed': '30 ft.',
                'strength': '16 (+3)',
                'strength_mod': '+3',
                'strength_save': '+3',
                'dexterity': '12 (+1)',
                'dexterity_mod': '+1',
                'dexterity_save': '+1',
                'constitution': '16 (+3)',
                'constitution_mod': '+3',
                'constitution_save': '+3',
                'intelligence': '7 (-2)',
                'intelligence_mod': '-2',
                'intelligence_save': '-2',
                'wisdom': '11 (+0)',
                'wisdom_mod': '+0',
                'wisdom_save': '+0',
                'charisma': '10 (+0)',
                'charisma_mod': '+0',
                'charisma_save': '+0',
                'senses': 'Darkvision 60 ft.',
                'languages': 'Common, Orc',
                'challenge_rating': 'CR 1/2',
                'actions': 'Greataxe. Melee Weapon Attack: +5 to hit, reach 5 ft., one target. Hit: 9 (1d12 + 3) slashing damage.'
            },
            {
                'name': 'Troll',
                'ac': 15,
                'initiative': '+1',
                'hp': '84 (8d10 + 40)',
                'speed': '30 ft.',
                'strength': '18 (+4)',
                'strength_mod': '+4',
                'strength_save': '+4',
                'dexterity': '13 (+1)',
                'dexterity_mod': '+1',
                'dexterity_save': '+1',
                'constitution': '20 (+5)',
                'constitution_mod': '+5',
                'constitution_save': '+5',
                'intelligence': '7 (-2)',
                'intelligence_mod': '-2',
                'intelligence_save': '-2',
                'wisdom': '9 (-1)',
                'wisdom_mod': '-1',
                'wisdom_save': '-1',
                'charisma': '7 (-2)',
                'charisma_mod': '-2',
                'charisma_save': '-2',
                'skills': 'Perception +2',
                'senses': 'Darkvision 60 ft.',
                'languages': 'Giant',
                'challenge_rating': 'CR 5',
                'traits': 'Regeneration. The troll regains 10 hit points at the start of its turn.',
                'actions': 'Multiattack. The troll makes three attacks: one with its bite and two with its claws.',
                'resistances': 'Bludgeoning, Piercing, and Slashing from Nonmagical Attacks'
            },
            {
                'name': 'Dragon (Young Red)',
                'ac': 18,
                'initiative': '+0',
                'hp': '178 (17d12 + 68)',
                'speed': '40 ft., climb 40 ft., fly 80 ft.',
                'strength': '23 (+6)',
                'strength_mod': '+6',
                'strength_save': '+9',
                'dexterity': '10 (+0)',
                'dexterity_mod': '+0',
                'dexterity_save': '+3',
                'constitution': '21 (+5)',
                'constitution_mod': '+5',
                'constitution_save': '+8',
                'intelligence': '14 (+2)',
                'intelligence_mod': '+2',
                'intelligence_save': '+5',
                'wisdom': '13 (+1)',
                'wisdom_mod': '+1',
                'wisdom_save': '+4',
                'charisma': '17 (+3)',
                'charisma_mod': '+3',
                'charisma_save': '+6',
                'skills': 'Perception +7, Stealth +3',
                'senses': 'Blindsight 30 ft., Darkvision 120 ft.',
                'languages': 'Common, Draconic',
                'challenge_rating': 'CR 10',
                'traits': 'Fire Immunity',
                'actions': 'Multiattack. The dragon makes three attacks: one with its bite and two with its claws.',
                'resistances': 'Fire'
            },
            {
                'name': 'Mind Flayer',
                'ac': 15,
                'initiative': '+7',
                'hp': '71 (13d8 + 13)',
                'speed': '30 ft.',
                'strength': '15 (+2)',
                'strength_mod': '+2',
                'strength_save': '+2',
                'dexterity': '12 (+1)',
                'dexterity_mod': '+1',
                'dexterity_save': '+1',
                'constitution': '13 (+1)',
                'constitution_mod': '+1',
                'constitution_save': '+1',
                'intelligence': '19 (+4)',
                'intelligence_mod': '+4',
                'intelligence_save': '+7',
                'wisdom': '17 (+3)',
                'wisdom_mod': '+3',
                'wisdom_save': '+6',
                'charisma': '17 (+3)',
                'charisma_mod': '+3',
                'charisma_save': '+6',
                'skills': 'Deception +6, Insight +6, Perception +6, Persuasion +6, Stealth +4',
                'senses': 'Darkvision 120 ft.',
                'languages': 'Deep Speech, Undercommon, telepathy 120 ft.',
                'challenge_rating': 'CR 7',
                'traits': 'Magic Resistance. The mind flayer has advantage on saving throws against spells and other magical effects.',
                'actions': 'Tentacles. Melee Weapon Attack: +7 to hit, reach 5 ft., one creature. Hit: 15 (2d10 + 4) psychic damage.'
            }
        ]
        
        monsters = []
        for i in range(min(count, len(monsters_data))):
            monster = Monster.objects.create(**monsters_data[i])
            monsters.append(monster)
        
        # Create additional random monsters if needed
        if count > len(monsters_data):
            for i in range(count - len(monsters_data)):
                monster = Monster.objects.create(
                    name=f'Random Monster {i+1}',
                    ac=random.randint(10, 20),
                    initiative=f'+{random.randint(0, 5)}',
                    hp=f'{random.randint(20, 100)} ({random.randint(4, 12)}d{random.randint(6, 12)} + {random.randint(10, 50)})',
                    speed='30 ft.',
                    strength=f'{random.randint(8, 20)} ({random.randint(-1, 5):+d})',
                    strength_mod=f'{random.randint(-1, 5):+d}',
                    strength_save=f'{random.randint(-1, 5):+d}',
                    dexterity=f'{random.randint(8, 20)} ({random.randint(-1, 5):+d})',
                    dexterity_mod=f'{random.randint(-1, 5):+d}',
                    dexterity_save=f'{random.randint(-1, 5):+d}',
                    constitution=f'{random.randint(8, 20)} ({random.randint(-1, 5):+d})',
                    constitution_mod=f'{random.randint(-1, 5):+d}',
                    constitution_save=f'{random.randint(-1, 5):+d}',
                    intelligence=f'{random.randint(8, 20)} ({random.randint(-1, 5):+d})',
                    intelligence_mod=f'{random.randint(-1, 5):+d}',
                    intelligence_save=f'{random.randint(-1, 5):+d}',
                    wisdom=f'{random.randint(8, 20)} ({random.randint(-1, 5):+d})',
                    wisdom_mod=f'{random.randint(-1, 5):+d}',
                    wisdom_save=f'{random.randint(-1, 5):+d}',
                    charisma=f'{random.randint(8, 20)} ({random.randint(-1, 5):+d})',
                    charisma_mod=f'{random.randint(-1, 5):+d}',
                    charisma_save=f'{random.randint(-1, 5):+d}',
                    senses='Darkvision 60 ft.',
                    languages='Common',
                    challenge_rating=f'CR {random.randint(1, 10)}',
                    actions='Basic attack with weapon.'
                )
                monsters.append(monster)
        
        return monsters

    def create_sessions(self, campaigns):
        """Create test game sessions"""
        sessions = []
        
        for campaign in campaigns:
            # Create 2-4 sessions per campaign
            num_sessions = random.randint(2, 4)
            base_date = date.today() - timedelta(days=30)
            
            for i in range(num_sessions):
                session_date = base_date + timedelta(days=i*7 + random.randint(0, 6))
                session = Session.objects.create(
                    campaign=campaign,
                    planning_notes=f'Session {i+1} planning notes for {campaign.title}. Prepare encounters, NPCs, and plot developments.',
                    session_notes=f'Session {i+1} recap: The party encountered various challenges and made important decisions that will affect the story.',
                    session_date=session_date
                )
                sessions.append(session)
        
        return sessions

    def create_encounters(self, campaigns, players, monsters):
        """Create test encounters"""
        encounters = []
        
        encounter_names = [
            'Goblin Ambush',
            'Orc War Party',
            'Troll Bridge',
            'Dragon\'s Lair',
            'Mind Flayer Colony',
            'Bandit Camp',
            'Undead Crypt',
            'Elemental Portal',
            'Giant Spider Nest',
            'Cultist Ritual'
        ]
        
        for campaign in campaigns:
            # Create 2-3 encounters per campaign
            num_encounters = random.randint(2, 3)
            campaign_players = [p for p in players if p.campaign == campaign]
            
            for i in range(num_encounters):
                encounter_name = random.choice(encounter_names)
                encounter = Encounter.objects.create(
                    name=f'{encounter_name} - {campaign.title}',
                    description=f'A challenging encounter featuring {encounter_name.lower()} in the {campaign.title} campaign.',
                    campaign=campaign
                )
                
                # Add random players from this campaign
                if campaign_players:
                    num_participants = min(random.randint(2, 4), len(campaign_players))
                    selected_players = random.sample(campaign_players, num_participants)
                    encounter.players.set(selected_players)
                
                # Add random monsters
                num_monsters = random.randint(1, 3)
                selected_monsters = random.sample(monsters, min(num_monsters, len(monsters)))
                encounter.monsters.set(selected_monsters)
                
                encounters.append(encounter)
        
        return encounters
