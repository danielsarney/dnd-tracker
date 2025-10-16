import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from accounts.models import TwoFactorCode
from campaigns.models import Campaign
from players.models import Player
from monsters.models import Monster
from combat_tracker.models import Encounter, CombatSession, CombatParticipant
from game_sessions.models import Session

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances"""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.LazyFunction(lambda: "+1234567890")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    two_factor_enabled = False
    two_factor_secret = ""
    is_active = True
    is_staff = False
    is_superuser = False


class UserWith2FAFactory(UserFactory):
    """Factory for creating User instances with 2FA enabled"""

    two_factor_enabled = True
    two_factor_secret = factory.LazyFunction(lambda: "JBSWY3DPEHPK3PXP")


class SuperUserFactory(UserFactory):
    """Factory for creating superuser instances"""

    is_staff = True
    is_superuser = True
    email = factory.Sequence(lambda n: f"admin{n}@example.com")
    username = factory.Sequence(lambda n: f"admin{n}")


class TwoFactorCodeFactory(factory.django.DjangoModelFactory):
    """Factory for creating TwoFactorCode instances"""

    class Meta:
        model = TwoFactorCode

    user = factory.SubFactory(UserFactory)
    code = factory.Sequence(lambda n: f"{100000 + n:06d}")
    created_at = factory.LazyFunction(timezone.now)
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(minutes=10))
    used = False


class ExpiredTwoFactorCodeFactory(TwoFactorCodeFactory):
    """Factory for creating expired TwoFactorCode instances"""

    expires_at = factory.LazyFunction(lambda: timezone.now() - timedelta(minutes=1))


class UsedTwoFactorCodeFactory(TwoFactorCodeFactory):
    """Factory for creating used TwoFactorCode instances"""

    used = True


class CampaignFactory(factory.django.DjangoModelFactory):
    """Factory for creating Campaign instances"""

    class Meta:
        model = Campaign

    title = factory.Sequence(lambda n: f"Campaign {n}")
    description = factory.Faker("text", max_nb_chars=500)
    introduction = factory.Faker("text", max_nb_chars=300)
    character_requirements = factory.Faker("text", max_nb_chars=400)


class PlayerFactory(factory.django.DjangoModelFactory):
    """Factory for creating Player instances"""

    class Meta:
        model = Player

    character_name = factory.Sequence(lambda n: f"Character {n}")
    player_name = factory.Faker("name")
    character_class = factory.Faker(
        "random_element", elements=["Fighter", "Wizard", "Rogue", "Cleric", "Paladin"]
    )
    subclass = factory.Faker(
        "random_element",
        elements=["Champion", "Evocation", "Assassin", "Life", "Devotion"],
    )
    race = factory.Faker(
        "random_element", elements=["Human", "Elf", "Dwarf", "Halfling", "Dragonborn"]
    )
    level = factory.Faker("random_int", min=1, max=20)
    ac = factory.Faker("random_int", min=10, max=20)
    background = factory.Faker("text", max_nb_chars=200)
    campaign = factory.SubFactory(CampaignFactory)


class MonsterFactory(factory.django.DjangoModelFactory):
    """Factory for creating Monster instances"""

    class Meta:
        model = Monster

    name = factory.Sequence(lambda n: f"Monster {n}")
    ac = factory.Faker("random_int", min=10, max=25)
    initiative = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )
    hp = factory.Faker("random_int", min=10, max=200)
    speed = factory.Faker(
        "random_element", elements=["30 ft", "40 ft", "50 ft", "60 ft"]
    )

    # Ability Scores
    strength = factory.Faker(
        "random_element", elements=["10", "12", "14", "16", "18", "20"]
    )
    strength_mod = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )
    strength_save = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )

    dexterity = factory.Faker(
        "random_element", elements=["10", "12", "14", "16", "18", "20"]
    )
    dexterity_mod = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )
    dexterity_save = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )

    constitution = factory.Faker(
        "random_element", elements=["10", "12", "14", "16", "18", "20"]
    )
    constitution_mod = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )
    constitution_save = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )

    intelligence = factory.Faker(
        "random_element", elements=["10", "12", "14", "16", "18", "20"]
    )
    intelligence_mod = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )
    intelligence_save = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )

    wisdom = factory.Faker(
        "random_element", elements=["10", "12", "14", "16", "18", "20"]
    )
    wisdom_mod = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )
    wisdom_save = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )

    charisma = factory.Faker(
        "random_element", elements=["10", "12", "14", "16", "18", "20"]
    )
    charisma_mod = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )
    charisma_save = factory.Faker(
        "random_element", elements=["+0", "+1", "+2", "+3", "+4", "+5"]
    )

    skills = factory.Faker("text", max_nb_chars=200)
    resistances = factory.Faker("text", max_nb_chars=100)
    immunities = factory.Faker("text", max_nb_chars=100)
    vulnerabilities = factory.Faker("text", max_nb_chars=100)
    senses = factory.Faker("text", max_nb_chars=100)
    languages = factory.Faker("text", max_nb_chars=100)
    gear = factory.Faker("text", max_nb_chars=200)
    challenge_rating = factory.Faker(
        "random_element", elements=["CR 1", "CR 2", "CR 3", "CR 4", "CR 5"]
    )
    traits = factory.Faker("text", max_nb_chars=300)
    actions = factory.Faker("text", max_nb_chars=300)
    bonus_actions = factory.Faker("text", max_nb_chars=200)
    reactions = factory.Faker("text", max_nb_chars=200)
    legendary_actions = factory.Faker("text", max_nb_chars=200)


class EncounterFactory(factory.django.DjangoModelFactory):
    """Factory for creating Encounter instances"""

    class Meta:
        model = Encounter

    name = factory.Sequence(lambda n: f"Encounter {n}")
    description = factory.Faker("text", max_nb_chars=300)
    campaign = factory.SubFactory(CampaignFactory)

    @factory.post_generation
    def players(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for player in extracted:
                self.players.add(player)
        else:
            # Add some random players
            players = PlayerFactory.create_batch(2, campaign=self.campaign)
            for player in players:
                self.players.add(player)

    @factory.post_generation
    def monsters(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for monster in extracted:
                self.monsters.add(monster)
        else:
            # Add some random monsters
            monsters = MonsterFactory.create_batch(2)
            for monster in monsters:
                self.monsters.add(monster)


class CombatSessionFactory(factory.django.DjangoModelFactory):
    """Factory for creating CombatSession instances"""

    class Meta:
        model = CombatSession

    encounter = factory.SubFactory(EncounterFactory)
    current_round = 1
    current_turn_index = 0
    is_active = True


class CombatParticipantFactory(factory.django.DjangoModelFactory):
    """Factory for creating CombatParticipant instances"""

    class Meta:
        model = CombatParticipant

    combat_session = factory.SubFactory(CombatSessionFactory)
    participant_type = factory.Faker("random_element", elements=["player", "monster"])
    initiative = factory.Faker("random_int", min=1, max=30)
    current_hp = factory.Faker("random_int", min=1, max=100)
    max_hp = factory.Faker("random_int", min=1, max=100)
    is_dead = False
    turn_completed = False

    @factory.lazy_attribute
    def player(self):
        if self.participant_type == "player":
            return PlayerFactory()
        return None

    @factory.lazy_attribute
    def monster(self):
        if self.participant_type == "monster":
            return MonsterFactory()
        return None


class SessionFactory(factory.django.DjangoModelFactory):
    """Factory for creating Session instances"""

    class Meta:
        model = Session

    campaign = factory.SubFactory(CampaignFactory)
    planning_notes = factory.Faker("text", max_nb_chars=500)
    session_notes = factory.Faker("text", max_nb_chars=600)
    session_date = factory.Faker("date_this_year")
