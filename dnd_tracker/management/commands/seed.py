from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from accounts.models import Profile
from campaigns.models import Campaign
from characters.models import Character
from game_sessions.models import GameSession
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with dummy data for testing and demo purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--campaigns',
            type=int,
            default=5,
            help='Number of campaigns to create (default: 5)'
        )
        parser.add_argument(
            '--characters',
            type=int,
            default=25,
            help='Number of characters to create (default: 25)'
        )
        parser.add_argument(
            '--sessions',
            type=int,
            default=30,
            help='Number of game sessions to create (default: 30)'
        )
        parser.add_argument(
            '--monsters',
            type=int,
            default=15,
            help='Number of monsters to create (default: 15)'
        )
        parser.add_argument(
            '--no-clear',
            action='store_true',
            default=False,
            help='Skip clearing existing data before seeding (default: clear data)'
        )

    def handle(self, *args, **options):
        if not options.get('no-clear', False):
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        self.stdout.write('Starting to seed database...')
        
        with transaction.atomic():
            users = self.create_users(options['users'])
            campaigns = self.create_campaigns(options['campaigns'], users)
            characters = self.create_characters(options['characters'], campaigns)
            monsters = self.create_monsters(options['monsters'], campaigns)
            sessions = self.create_game_sessions(options['sessions'], campaigns)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'- {len(users)} users\n'
                f'- {len(campaigns)} campaigns\n'
                f'- {len(characters)} characters\n'
                f'- {len(monsters)} monsters\n'
                f'- {len(sessions)} game sessions'
            )
        )

    def clear_data(self):
        """Clear all existing data"""
        GameSession.objects.all().delete()
        Character.objects.all().delete()
        Campaign.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('Existing data cleared.')

    def create_users(self, count):
        """Create dummy users with profiles"""
        users = []
        first_names = [
            'Aiden', 'Bella', 'Caleb', 'Diana', 'Ethan', 'Fiona', 'Gavin', 'Hannah',
            'Ian', 'Jade', 'Kai', 'Luna', 'Mason', 'Nova', 'Owen', 'Peyton',
            'Quinn', 'Riley', 'Sage', 'Tyler', 'Uma', 'Violet', 'Wyatt', 'Xena',
            'Yuki', 'Zara', 'Alex', 'Blake', 'Casey', 'Drew', 'Emery', 'Finley'
        ]
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin'
        ]
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}{last_name.lower()}{i+1}"
            email = f"{username}@example.com"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            
            # Update profile with display name
            profile = user.profile
            profile.display_name = f"{first_name} {last_name}"
            profile.save()
            
            users.append(user)
            
        self.stdout.write(f'Created {len(users)} users')
        return users

    def create_campaigns(self, count, users):
        """Create dummy campaigns"""
        campaigns = []
        campaign_names = [
            'The Lost Mines of Phandelver',
            'Curse of Strahd',
            'Storm King\'s Thunder',
            'Tomb of Annihilation',
            'Waterdeep: Dragon Heist',
            'Out of the Abyss',
            'Princes of the Apocalypse',
            'Hoard of the Dragon Queen',
            'Rise of Tiamat',
            'Ghosts of Saltmarsh',
            'Descent into Avernus',
            'Icewind Dale: Rime of the Frostmaiden',
            'The Wild Beyond the Witchlight',
            'Strixhaven: A Curriculum of Chaos',
            'Spelljammer: Adventures in Space'
        ]
        
        campaign_descriptions = [
            'A classic adventure for new players and DMs alike.',
            'A gothic horror adventure in the land of Barovia.',
            'Giants threaten the North with their ancient magic.',
            'Death lurks in the jungles of Chult.',
            'A treasure hunt in the City of Splendors.',
            'Escape from the Underdark\'s depths.',
            'Elemental cults threaten the Dessarin Valley.',
            'Dragons have returned to the Realms.',
            'The Cult of the Dragon grows stronger.',
            'Maritime adventures along the Sword Coast.',
            'A journey into the Nine Hells.',
            'Survive the endless winter of Icewind Dale.',
            'A whimsical adventure in the Feywild.',
            'Magical education at the greatest school of magic.',
            'Space-faring adventures among the stars.'
        ]
        
        for i in range(count):
            name = random.choice(campaign_names)
            description = random.choice(campaign_descriptions)
            dm = random.choice(users).get_full_name() or random.choice(users).username
            
            campaign = Campaign.objects.create(
                name=name,
                description=description,
                dm=dm
            )
            campaigns.append(campaign)
            
        self.stdout.write(f'Created {len(campaigns)} campaigns')
        return campaigns

    def create_characters(self, count, campaigns):
        """Create dummy characters"""
        characters = []
        races = [
            'Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 'Gnome',
            'Half-Elf', 'Half-Orc', 'Tiefling', 'Aasimar', 'Goliath',
            'Firbolg', 'Kenku', 'Lizardfolk', 'Tabaxi', 'Triton'
        ]
        
        classes = [
            'Fighter', 'Wizard', 'Cleric', 'Rogue', 'Ranger', 'Paladin',
            'Barbarian', 'Bard', 'Druid', 'Monk', 'Sorcerer', 'Warlock',
            'Artificer', 'Blood Hunter'
        ]
        
        backgrounds = [
            'Acolyte', 'Criminal', 'Folk Hero', 'Noble', 'Sage', 'Soldier',
            'Urchin', 'Entertainer', 'Guild Artisan', 'Hermit', 'Outlander',
            'Charlatan', 'City Watch', 'Clan Crafter', 'Courtier', 'Faction Agent'
        ]
        
        character_names = [
            'Thorin Ironfist', 'Lyra Silverwind', 'Grimtooth', 'Zephyr Swift',
            'Morgrim Stonebeard', 'Elara Nightshade', 'Krag Thunderfist',
            'Seraphina Bright', 'Raven Shadow', 'Brom Ironheart', 'Nyx Void',
            'Aria Songweaver', 'Garrick Storm', 'Luna Moonwhisper', 'Drax Bloodaxe',
            'Vesper Star', 'Kael Firebrand', 'Mira Frost', 'Thorne Blackwood',
            'Sylvana Leaf', 'Rook Ravenshadow', 'Ember Flame', 'Caspian Wave',
            'Nova Lightbringer', 'Shadow Fang', 'Aurora Dawn', 'Vex Thunder',
            'Iris Petal', 'Orion Star', 'Phoenix Ash'
        ]
        
        for i in range(count):
            campaign = random.choice(campaigns)
            character_type = random.choices(['PLAYER', 'NPC'], weights=[0.7, 0.3])[0]
            name = random.choice(character_names)
            race = random.choice(races)
            character_class = random.choice(classes)
            background = random.choice(backgrounds)
            
            character = Character.objects.create(
                campaign=campaign,
                type=character_type,
                name=name,
                race=race,
                character_class=character_class,
                background=f"A {race} {character_class} with a {background} background."
            )
            characters.append(character)
            
        self.stdout.write(f'Created {len(characters)} characters')
        return characters

    def create_monsters(self, count, campaigns):
        """Create dummy monsters"""
        monsters = []
        monster_names = [
            'Goblin', 'Orc', 'Troll', 'Dragon', 'Giant Spider', 'Skeleton',
            'Zombie', 'Wraith', 'Vampire', 'Werewolf', 'Minotaur', 'Cyclops',
            'Harpy', 'Medusa', 'Chimera', 'Griffon', 'Pegasus', 'Unicorn',
            'Basilisk', 'Cockatrice', 'Manticore', 'Hydra', 'Kraken', 'Lich',
            'Beholder', 'Mind Flayer', 'Githyanki', 'Drow', 'Duergar', 'Svirfneblin',
            'Kobold', 'Gnoll', 'Bugbear', 'Hobgoblin', 'Ogre', 'Ettin',
            'Hill Giant', 'Frost Giant', 'Fire Giant', 'Cloud Giant', 'Storm Giant',
            'Red Dragon', 'Blue Dragon', 'Green Dragon', 'Black Dragon', 'White Dragon',
            'Gold Dragon', 'Silver Dragon', 'Bronze Dragon', 'Copper Dragon', 'Brass Dragon',
            'Demon', 'Devil', 'Angel', 'Elemental', 'Golem', 'Construct',
            'Shadow', 'Ghost', 'Specter', 'Banshee', 'Wight', 'Mummy',
            'Lich', 'Vampire Lord', 'Werewolf Alpha', 'Dragon Turtle', 'Roc',
            'Purple Worm', 'Remorhaz', 'Bulette', 'Rust Monster', 'Displacer Beast',
            'Owlbear', 'Dire Wolf', 'Dire Bear', 'Dire Tiger', 'Dire Lion',
            'Giant Eagle', 'Giant Owl', 'Giant Bat', 'Giant Rat', 'Giant Scorpion',
            'Giant Centipede', 'Giant Spider', 'Giant Wasp', 'Giant Ant', 'Giant Bee'
        ]
        
        monster_types = [
            'Beast', 'Humanoid', 'Undead', 'Dragon', 'Giant', 'Elemental',
            'Fiend', 'Celestial', 'Aberration', 'Construct', 'Monstrosity',
            'Plant', 'Fey', 'Ooze', 'Swarm'
        ]
        
        monster_descriptions = [
            'A fearsome creature that lurks in the shadows.',
            'A massive beast with incredible strength and ferocity.',
            'An ancient creature of legend and myth.',
            'A cunning predator that hunts in packs.',
            'A magical creature with otherworldly powers.',
            'A corrupted being twisted by dark magic.',
            'A guardian spirit bound to protect ancient secrets.',
            'A fallen creature seeking redemption or revenge.',
            'A primordial force of nature given form.',
            'A twisted experiment gone horribly wrong.',
            'A noble creature corrupted by evil influences.',
            'A mysterious entity from beyond the material plane.',
            'A legendary beast that few have lived to tell about.',
            'A guardian of ancient treasures and forgotten knowledge.',
            'A creature of pure elemental energy.',
            'A shapeshifting predator that adapts to its prey.',
            'A massive creature that towers over the landscape.',
            'A flying predator that rules the skies.',
            'A subterranean horror that haunts the deep places.',
            'A magical construct brought to life by ancient magic.'
        ]
        
        for i in range(count):
            campaign = random.choice(campaigns)
            name = random.choice(monster_names)
            monster_type = random.choice(monster_types)
            description = random.choice(monster_descriptions)
            
            # Add some variety to monster names
            if random.random() < 0.3:  # 30% chance to add a descriptor
                descriptors = ['Ancient', 'Giant', 'Dire', 'Shadow', 'Frost', 'Fire', 'Storm', 'Dark', 'Cursed', 'Blessed']
                name = f"{random.choice(descriptors)} {name}"
            
            monster = Character.objects.create(
                campaign=campaign,
                type='MONSTER',
                name=name,
                race=monster_type,
                character_class='Monster',
                background=description
            )
            monsters.append(monster)
            
        self.stdout.write(f'Created {len(monsters)} monsters')
        return monsters

    def create_game_sessions(self, count, campaigns):
        """Create dummy game sessions"""
        sessions = []
        session_summaries = [
            'The party arrived at the small town of Phandalin and learned about the missing dwarven miners.',
            'A mysterious fog descended upon the village, and strange creatures began appearing at night.',
            'The adventurers discovered an ancient temple hidden beneath the ruins of a forgotten city.',
            'A powerful dragon attacked the settlement, forcing the heroes to defend the innocent.',
            'The party ventured into the Underdark in search of a missing noble.',
            'Ancient magic awakened in the forest, causing the trees to move and speak.',
            'The heroes uncovered a conspiracy involving corrupt city officials and criminal organizations.',
            'A magical storm trapped the party in an abandoned wizard\'s tower.',
            'The adventurers discovered a portal to another plane of existence.',
            'A mysterious artifact began corrupting those who touched it.',
            'The party encountered a group of friendly goblins who needed help.',
            'An ancient curse began affecting the local population.',
            'The heroes discovered a hidden library containing forbidden knowledge.',
            'A powerful necromancer raised an army of undead.',
            'The party found themselves in the middle of a war between two feuding kingdoms.',
            'A magical disease began spreading through the city.',
            'The adventurers discovered a hidden entrance to a dwarven stronghold.',
            'Ancient guardians awakened to test the party\'s worthiness.',
            'The heroes found themselves trapped in a time loop.',
            'A powerful artifact began affecting the weather patterns.',
            'The party discovered a hidden village of peaceful monsters.',
            'An ancient prophecy began to unfold.',
            'The heroes encountered a group of traveling merchants with suspicious goods.',
            'A magical barrier appeared around the city.',
            'The party discovered a hidden passage in the castle dungeons.',
            'Ancient runes began glowing with mysterious power.',
            'The heroes found themselves in a pocket dimension.',
            'A powerful spellcaster challenged the party to a magical duel.',
            'The party discovered a hidden treasury beneath the city.',
            'Ancient spirits began appearing to guide the heroes.'
        ]
        
        # Generate dates for the last 6 months
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=180)
        
        for i in range(count):
            campaign = random.choice(campaigns)
            # Random date within the last 6 months
            days_ago = random.randint(0, 180)
            session_date = end_date - timedelta(days=days_ago)
            summary = random.choice(session_summaries)
            
            session = GameSession.objects.create(
                campaign=campaign,
                date=session_date,
                summary=summary
            )
            sessions.append(session)
            
        self.stdout.write(f'Created {len(sessions)} game sessions')
        return sessions
