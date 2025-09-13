from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from accounts.models import Profile
from campaigns.models import Campaign
from characters.models import Character
from game_sessions.models import GameSession
from planning.models import PlanningSession
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
            '--planning',
            type=int,
            default=20,
            help='Number of planning sessions to create (default: 20)'
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
            planning_sessions = self.create_planning_sessions(options['planning'], campaigns)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'- {len(users)} users\n'
                f'- {len(campaigns)} campaigns\n'
                f'- {len(characters)} characters\n'
                f'- {len(monsters)} monsters\n'
                f'- {len(sessions)} game sessions\n'
                f'- {len(planning_sessions)} planning sessions'
            )
        )

    def clear_data(self):
        """Clear all existing data"""
        # Clear in reverse dependency order to avoid foreign key constraints
        PlanningSession.objects.all().delete()
        GameSession.objects.all().delete()
        Character.objects.all().delete()
        Campaign.objects.all().delete()
        
        # Clear profiles and users
        Profile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Reset sequences to avoid ID conflicts
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT setval(pg_get_serial_sequence('accounts_profile', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('auth_user', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('campaigns_campaign', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('characters_character', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('game_sessions_gamesession', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('planning_planningsession', 'id'), 1, false);")
        
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
            display_name = f"{first_name} {last_name}"
            
            # Ensure unique display name
            counter = 1
            original_display_name = display_name
            while Profile.objects.filter(display_name=display_name).exists():
                display_name = f"{original_display_name} {counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            
            # Update profile with unique display name
            profile = user.profile
            profile.display_name = display_name
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

    def create_planning_sessions(self, count, campaigns):
        """Create dummy planning sessions"""
        planning_sessions = []
        planning_titles = [
            'The Goblin Cave', 'City of Shadows', 'Dragon\'s Lair', 'Ancient Temple',
            'The Lost Library', 'Underdark Depths', 'Feywild Portal', 'Necromancer\'s Tower',
            'Pirate Cove', 'Frozen Wasteland', 'Desert Oasis', 'Mountain Pass',
            'Haunted Manor', 'Wizard\'s Laboratory', 'Thieves\' Guild', 'Royal Palace',
            'Abandoned Mine', 'Cursed Forest', 'Volcanic Crater', 'Crystal Caverns',
            'Floating Islands', 'Shadow Realm', 'Elemental Plane', 'Astral Sea',
            'Time Distortion', 'Memory Palace', 'Dream Realm', 'Void Between Worlds',
            'Celestial Court', 'Infernal Pit', 'Abyssal Depths', 'Paradise Lost',
            'The Final Battle', 'Epic Confrontation', 'Climactic Showdown', 'Ultimate Test',
            'New Beginnings', 'Fresh Start', 'Next Chapter', 'Future Adventures'
        ]
        
        planning_notes_templates = [
            "## Session Overview\nThis session will focus on {focus}. The party should encounter {encounter} and potentially discover {discovery}.\n\n## Key NPCs\n- {npc1}: {description1}\n- {npc2}: {description2}\n\n## Encounters\n1. **{encounter1}**: {description3}\n2. **{encounter2}**: {description4}\n\n## Locations\n- **{location1}**: {description5}\n- **{location2}**: {description6}\n\n## Plot Points\n- {plot1}\n- {plot2}\n- {plot3}\n\n## Combat Notes\n- {combat1}\n- {combat2}\n\n## Treasure\n- {treasure1}\n- {treasure2}\n\n## Notes\n{additional_notes}",
            
            "## Preparation Checklist\n- [ ] Review character backstories\n- [ ] Prepare battle maps\n- [ ] Set up miniatures\n- [ ] Review NPC motivations\n- [ ] Check spell effects\n- [ ] Prepare music/ambiance\n\n## Session Goals\n1. {goal1}\n2. {goal2}\n3. {goal3}\n\n## Expected Challenges\n- {challenge1}\n- {challenge2}\n\n## Backup Plans\n- If players go off track: {backup1}\n- If combat goes too long: {backup2}\n- If players miss clues: {backup3}\n\n## Environmental Details\n- Weather: {weather}\n- Lighting: {lighting}\n- Sounds: {sounds}\n- Smells: {smells}\n\n## Roleplay Opportunities\n- {rp1}\n- {rp2}\n- {rp3}",
            
            "## The Adventure Begins\n\n### Opening Scene\n{opening_scene}\n\n### Main Quest\n{main_quest}\n\n### Side Quests\n- {side1}\n- {side2}\n\n### Key Locations\n1. **{loc1}**: {desc1}\n2. **{loc2}**: {desc2}\n3. **{loc3}**: {desc3}\n\n### Important NPCs\n- **{npc1}**: {npc_desc1}\n- **{npc2}**: {npc_desc2}\n- **{npc3}**: {npc_desc3}\n\n### Combat Encounters\n- **Easy**: {easy_encounter}\n- **Medium**: {medium_encounter}\n- **Hard**: {hard_encounter}\n\n### Puzzles & Traps\n- {puzzle1}\n- {trap1}\n\n### Treasure & Rewards\n- {treasure1}\n- {treasure2}\n\n### Session End Hooks\n- {hook1}\n- {hook2}",
            
            "## DM Notes\n\n### Session Theme\n{theme}\n\n### Mood & Atmosphere\n{mood}\n\n### Key Moments\n1. {moment1}\n2. {moment2}\n3. {moment3}\n\n### Character Development\n- {char_dev1}\n- {char_dev2}\n\n### World Building\n- {world1}\n- {world2}\n\n### Foreshadowing\n- {foreshadow1}\n- {foreshadow2}\n\n### Potential Complications\n- {complication1}\n- {complication2}\n\n### Success Conditions\n- {success1}\n- {success2}\n\n### Failure Consequences\n- {failure1}\n- {failure2}\n\n### Random Events\n- {random1}\n- {random2}\n\n### Session Wrap-up\n{wrap_up}"
        ]
        
        # Generate dates for the next 3 months (planning sessions are typically for future sessions)
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=90)
        
        for i in range(count):
            campaign = random.choice(campaigns)
            # Random date within the next 3 months
            days_ahead = random.randint(1, 90)
            session_date = start_date + timedelta(days=days_ahead)
            title = random.choice(planning_titles)
            
            # Choose a random template and fill it with random content
            template = random.choice(planning_notes_templates)
            
            # Generate random content for the template
            content_vars = {
                'focus': random.choice(['exploration', 'combat', 'roleplay', 'puzzle solving', 'investigation', 'social interaction']),
                'encounter': random.choice(['goblins', 'bandits', 'a dragon', 'undead', 'elementals', 'a trap', 'a puzzle', 'a social challenge']),
                'discovery': random.choice(['ancient ruins', 'a hidden treasure', 'a secret passage', 'forbidden knowledge', 'a magical artifact', 'a lost civilization']),
                'npc1': random.choice(['Gareth the Guard', 'Mira the Merchant', 'Thorin the Blacksmith', 'Luna the Librarian', 'Grim the Guide']),
                'description1': random.choice(['A gruff but kind-hearted veteran', 'A cunning trader with many secrets', 'A master craftsman with a mysterious past', 'A wise scholar of ancient lore', 'A weathered guide who knows the area well']),
                'npc2': random.choice(['Elena the Enchantress', 'Marcus the Mage', 'Sara the Scout', 'Derek the Diplomat', 'Zara the Zealot']),
                'description2': random.choice(['A mysterious spellcaster with hidden motives', 'A scholarly wizard seeking knowledge', 'A stealthy ranger with keen senses', 'A smooth-talking negotiator', 'A religious fanatic with strong beliefs']),
                'encounter1': random.choice(['Goblin Ambush', 'Bandit Roadblock', 'Dragon Encounter', 'Undead Horde', 'Elemental Storm', 'Trap Room', 'Puzzle Chamber', 'Social Challenge']),
                'description3': random.choice(['A surprise attack from the shadows', 'A roadblock demanding payment', 'A fearsome dragon blocking the path', 'A horde of undead rising from the ground', 'A magical storm of elemental energy', 'A deadly trap room with multiple hazards', 'A complex puzzle requiring intelligence', 'A social situation requiring diplomacy']),
                'encounter2': random.choice(['Boss Battle', 'Environmental Hazard', 'Stealth Mission', 'Negotiation', 'Escape Sequence', 'Rescue Mission', 'Investigation', 'Exploration']),
                'description4': random.choice(['A climactic battle with the main antagonist', 'A dangerous environmental challenge', 'A stealth-based encounter requiring silence', 'A diplomatic negotiation with high stakes', 'An exciting escape from a collapsing area', 'A heroic rescue mission', 'A mystery requiring investigation', 'An exploration of unknown territory']),
                'location1': random.choice(['The Goblin Cave', 'The Ancient Temple', 'The Dragon\'s Lair', 'The Lost Library', 'The Underdark Depths']),
                'description5': random.choice(['A dark and dangerous cave system', 'An ancient temple filled with mysteries', 'A massive dragon\'s lair with treasure', 'A hidden library of forbidden knowledge', 'The deep and dangerous Underdark']),
                'location2': random.choice(['The City of Shadows', 'The Feywild Portal', 'The Necromancer\'s Tower', 'The Pirate Cove', 'The Frozen Wasteland']),
                'description6': random.choice(['A mysterious city shrouded in darkness', 'A portal to the magical Feywild', 'A tower of a powerful necromancer', 'A hidden cove used by pirates', 'A frozen wasteland of eternal winter']),
                'plot1': random.choice(['The party discovers a hidden conspiracy', 'An ancient prophecy begins to unfold', 'A powerful artifact is revealed', 'A long-lost relative is found', 'A terrible secret is uncovered']),
                'plot2': random.choice(['The villain\'s true identity is revealed', 'A major character betrays the party', 'A new ally joins the group', 'An old enemy returns', 'A great power is unleashed']),
                'plot3': random.choice(['The fate of the world hangs in the balance', 'A difficult choice must be made', 'A sacrifice is required', 'A great journey begins', 'An era comes to an end']),
                'combat1': random.choice(['Use terrain to your advantage', 'Focus fire on the biggest threat', 'Protect the spellcasters', 'Use crowd control abilities', 'Coordinate attacks for maximum effect']),
                'combat2': random.choice(['Watch for environmental hazards', 'Don\'t forget about opportunity attacks', 'Use cover and concealment', 'Manage spell slots carefully', 'Keep an eye on the battlefield']),
                'treasure1': random.choice(['A magical sword', 'A bag of holding', 'A ring of protection', 'A scroll of fireball', 'A potion of healing']),
                'treasure2': random.choice(['A cloak of elvenkind', 'A wand of magic missiles', 'A shield of faith', 'A gem of seeing', 'A rope of climbing']),
                'additional_notes': random.choice(['Remember to keep the pace moving', 'Don\'t forget to describe the environment', 'Give each player a moment to shine', 'Be prepared to improvise', 'Have fun and keep it engaging']),
                'goal1': random.choice(['Complete the main quest objective', 'Gather information about the villain', 'Rescue the captured NPC', 'Retrieve the stolen artifact', 'Defeat the boss monster']),
                'goal2': random.choice(['Explore the new area thoroughly', 'Make important social connections', 'Learn about the world\'s history', 'Gather resources for the journey', 'Prepare for the next challenge']),
                'goal3': random.choice(['Ensure all party members survive', 'Maintain the group\'s reputation', 'Discover hidden secrets', 'Build relationships with NPCs', 'Advance the overall story']),
                'challenge1': random.choice(['A difficult combat encounter', 'A complex puzzle or riddle', 'A social situation requiring diplomacy', 'A stealth mission with high stakes', 'A moral dilemma with no easy answer']),
                'challenge2': random.choice(['Environmental hazards and obstacles', 'Time pressure and deadlines', 'Limited resources or information', 'Conflicting goals and priorities', 'Unexpected complications and twists']),
                'backup1': random.choice(['Guide them back with an NPC', 'Introduce a new plot hook', 'Present an alternative path', 'Use environmental cues', 'Ask what their characters would do']),
                'backup2': random.choice(['Skip to the next scene', 'Use a deus ex machina', 'Introduce reinforcements', 'Change the encounter difficulty', 'Move to roleplay instead']),
                'backup3': random.choice(['Have an NPC provide hints', 'Use environmental storytelling', 'Give them another chance', 'Present the information differently', 'Ask for investigation checks']),
                'weather': random.choice(['Clear and sunny', 'Overcast and gloomy', 'Rainy and wet', 'Foggy and mysterious', 'Stormy and dramatic']),
                'lighting': random.choice(['Bright daylight', 'Dim torchlight', 'Magical illumination', 'Moonlight', 'Complete darkness']),
                'sounds': random.choice(['Birds chirping', 'Wind howling', 'Water flowing', 'Distant thunder', 'Eerie silence']),
                'smells': random.choice(['Fresh air', 'Damp earth', 'Smoke and ash', 'Flowers blooming', 'Something rotting']),
                'rp1': random.choice(['Character backstory moments', 'NPC interactions', 'Party bonding time', 'Moral discussions', 'Comic relief']),
                'rp2': random.choice(['Romantic subplots', 'Family reunions', 'Old rivalries', 'New friendships', 'Political intrigue']),
                'rp3': random.choice(['Philosophical debates', 'Cultural exchanges', 'Personal growth', 'Emotional moments', 'Comic misunderstandings']),
                'opening_scene': random.choice(['The party arrives at a bustling marketplace', 'A mysterious stranger approaches the group', 'The heroes find themselves in a dangerous situation', 'An old friend calls for help', 'A new adventure begins with a bang']),
                'main_quest': random.choice(['Stop the evil cult from summoning a demon', 'Find the lost artifact before the villains do', 'Rescue the kidnapped princess', 'Investigate the mysterious disappearances', 'Prevent the ancient curse from spreading']),
                'side1': random.choice(['Help the local blacksmith with a problem', 'Investigate the haunted house', 'Find the missing merchant\'s goods', 'Settle a dispute between two families', 'Explore the abandoned mine']),
                'side2': random.choice(['Deliver a message to a distant town', 'Help the local innkeeper with a pest problem', 'Find ingredients for a local alchemist', 'Investigate strange lights in the forest', 'Help a farmer with his crops']),
                'loc1': random.choice(['The Goblin Cave', 'The Ancient Temple', 'The Dragon\'s Lair', 'The Lost Library', 'The Underdark Depths']),
                'desc1': random.choice(['A dark and dangerous cave system', 'An ancient temple filled with mysteries', 'A massive dragon\'s lair with treasure', 'A hidden library of forbidden knowledge', 'The deep and dangerous Underdark']),
                'loc2': random.choice(['The City of Shadows', 'The Feywild Portal', 'The Necromancer\'s Tower', 'The Pirate Cove', 'The Frozen Wasteland']),
                'desc2': random.choice(['A mysterious city shrouded in darkness', 'A portal to the magical Feywild', 'A tower of a powerful necromancer', 'A hidden cove used by pirates', 'A frozen wasteland of eternal winter']),
                'loc3': random.choice(['The Royal Palace', 'The Thieves\' Guild', 'The Wizard\'s Laboratory', 'The Haunted Manor', 'The Crystal Caverns']),
                'desc3': random.choice(['A grand palace with many secrets', 'A hidden guild of skilled thieves', 'A magical laboratory filled with experiments', 'A haunted manor with a dark past', 'Beautiful caverns filled with crystals']),
                'npc1': random.choice(['Gareth the Guard', 'Mira the Merchant', 'Thorin the Blacksmith', 'Luna the Librarian', 'Grim the Guide']),
                'npc_desc1': random.choice(['A gruff but kind-hearted veteran', 'A cunning trader with many secrets', 'A master craftsman with a mysterious past', 'A wise scholar of ancient lore', 'A weathered guide who knows the area well']),
                'npc2': random.choice(['Elena the Enchantress', 'Marcus the Mage', 'Sara the Scout', 'Derek the Diplomat', 'Zara the Zealot']),
                'npc_desc2': random.choice(['A mysterious spellcaster with hidden motives', 'A scholarly wizard seeking knowledge', 'A stealthy ranger with keen senses', 'A smooth-talking negotiator', 'A religious fanatic with strong beliefs']),
                'npc3': random.choice(['Captain Blackbeard', 'The Oracle', 'The Hermit', 'The Jester', 'The Sage']),
                'npc_desc3': random.choice(['A legendary pirate with many tales', 'A mystical seer who knows the future', 'A wise hermit living in isolation', 'A court jester with hidden wisdom', 'An ancient sage with vast knowledge']),
                'easy_encounter': random.choice(['A few goblins', 'Some bandits', 'Wild animals', 'Minor undead', 'Simple traps']),
                'medium_encounter': random.choice(['A group of orcs', 'A pack of wolves', 'A troll', 'A group of skeletons', 'A magical construct']),
                'hard_encounter': random.choice(['A dragon', 'A lich', 'A demon', 'A group of giants', 'A powerful spellcaster']),
                'puzzle1': random.choice(['A riddle that must be solved', 'A pattern that must be recognized', 'A sequence that must be followed', 'A word that must be spoken', 'A symbol that must be drawn']),
                'trap1': random.choice(['A pressure plate that triggers darts', 'A false floor that opens to a pit', 'A magical ward that causes damage', 'A poison gas that fills the room', 'A rolling boulder that chases intruders']),
                'treasure1': random.choice(['A magical sword', 'A bag of holding', 'A ring of protection', 'A scroll of fireball', 'A potion of healing']),
                'treasure2': random.choice(['A cloak of elvenkind', 'A wand of magic missiles', 'A shield of faith', 'A gem of seeing', 'A rope of climbing']),
                'hook1': random.choice(['A mysterious letter arrives', 'An old enemy returns', 'A new threat emerges', 'A valuable opportunity presents itself', 'A personal quest begins']),
                'hook2': random.choice(['The party gains a new ally', 'A major secret is revealed', 'A great power is discovered', 'A difficult choice must be made', 'The adventure takes an unexpected turn']),
                'theme': random.choice(['Good vs. Evil', 'Redemption', 'Discovery', 'Sacrifice', 'Friendship', 'Power', 'Justice', 'Freedom']),
                'mood': random.choice(['Dark and mysterious', 'Light and hopeful', 'Epic and grand', 'Intimate and personal', 'Humorous and light', 'Tense and dramatic', 'Melancholy and reflective', 'Exciting and adventurous']),
                'moment1': random.choice(['A character makes a heroic sacrifice', 'The party discovers a shocking truth', 'A beloved NPC is lost', 'The heroes achieve a great victory', 'A new alliance is formed']),
                'moment2': random.choice(['A character faces their greatest fear', 'The party must make a difficult choice', 'A long-lost friend is reunited', 'A powerful enemy is defeated', 'A new quest begins']),
                'moment3': random.choice(['The party learns about their destiny', 'A character undergoes a transformation', 'The heroes save the day', 'A new threat is revealed', 'The adventure comes to an end']),
                'char_dev1': random.choice(['A character learns to trust others', 'A hero discovers their true power', 'A character faces their past', 'A hero learns to forgive', 'A character finds their purpose']),
                'char_dev2': random.choice(['A character grows stronger', 'A hero becomes wiser', 'A character learns humility', 'A hero gains confidence', 'A character finds peace']),
                'world1': random.choice(['The history of the realm is revealed', 'New lands are discovered', 'Ancient secrets are uncovered', 'The political landscape changes', 'Magic returns to the world']),
                'world2': random.choice(['A new civilization is found', 'An old empire falls', 'The balance of power shifts', 'New threats emerge', 'Hope is restored']),
                'foreshadow1': random.choice(['A mysterious figure watches from the shadows', 'An ancient prophecy is mentioned', 'A powerful artifact is glimpsed', 'A dark omen appears', 'A strange dream is had']),
                'foreshadow2': random.choice(['A character has a vision', 'An old legend is told', 'A warning is given', 'A sign appears in the sky', 'A voice speaks from nowhere']),
                'complication1': random.choice(['The party is betrayed', 'A powerful enemy appears', 'A natural disaster strikes', 'A magical curse is unleashed', 'A war breaks out']),
                'complication2': random.choice(['Resources become scarce', 'Allies turn against the party', 'The quest becomes more dangerous', 'Time runs out', 'The stakes are raised']),
                'success1': random.choice(['Complete the main objective', 'Save the innocent', 'Defeat the villain', 'Retrieve the artifact', 'Restore peace']),
                'success2': random.choice(['Gain valuable knowledge', 'Make new allies', 'Discover new lands', 'Uncover the truth', 'Achieve personal growth']),
                'failure1': random.choice(['The villain succeeds', 'Innocent people die', 'The artifact is lost', 'War breaks out', 'Darkness spreads']),
                'failure2': random.choice(['The party is captured', 'A city is destroyed', 'A curse is unleashed', 'An ancient evil awakens', 'Hope is lost']),
                'random1': random.choice(['A traveling merchant arrives', 'A storm rolls in', 'A wild animal appears', 'A shooting star falls', 'A mysterious fog descends']),
                'random2': random.choice(['A bard tells a tale', 'A festival begins', 'A tournament is announced', 'A ship arrives', 'A message is delivered']),
                'wrap_up': random.choice(['The party rests and recovers', 'New information is gathered', 'Plans are made for the future', 'The adventure continues', 'The story reaches a conclusion'])
            }
            
            # Fill in the template with random content
            notes = template.format(**content_vars)
            
            planning_session = PlanningSession.objects.create(
                campaign=campaign,
                session_date=session_date,
                title=title,
                notes=notes
            )
            planning_sessions.append(planning_session)
            
        self.stdout.write(f'Created {len(planning_sessions)} planning sessions')
        return planning_sessions
