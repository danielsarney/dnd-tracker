from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from dnd_tracker.factories import (
    UserFactory,
    CampaignFactory,
    PlayerFactory,
    MonsterFactory,
    EncounterFactory,
    CombatSessionFactory,
    CombatParticipantFactory,
)
from combat_tracker.models import Encounter, CombatSession, CombatParticipant
from combat_tracker.forms import EncounterForm, InitiativeForm, HPTrackingForm
from combat_tracker.views import parse_monster_hp

User = get_user_model()


class CombatTrackerModelTest(TestCase):
    """Test cases for combat_tracker models"""

    def setUp(self):
        """Set up test data"""
        self.campaign = CampaignFactory()
        self.player = PlayerFactory(campaign=self.campaign)
        self.monster = MonsterFactory()
        self.encounter = EncounterFactory(campaign=self.campaign)
        self.encounter.players.add(self.player)
        self.encounter.monsters.add(self.monster)

    def test_encounter_creation(self):
        """Test that an encounter can be created with all fields"""
        self.assertIsInstance(self.encounter, Encounter)
        self.assertTrue(self.encounter.name)
        self.assertTrue(self.encounter.description)
        self.assertEqual(self.encounter.campaign, self.campaign)
        self.assertIn(self.player, self.encounter.players.all())
        self.assertIn(self.monster, self.encounter.monsters.all())

    def test_encounter_str_representation(self):
        """Test the string representation of Encounter"""
        expected = f"{self.encounter.name} ({self.campaign.title})"
        self.assertEqual(str(self.encounter), expected)

    def test_encounter_ordering(self):
        """Test that encounters are ordered by created_at descending"""
        encounter1 = EncounterFactory(campaign=self.campaign)
        encounter2 = EncounterFactory(campaign=self.campaign)

        encounters = Encounter.objects.all()
        # Most recent first
        self.assertEqual(encounters[0], encounter2)
        self.assertEqual(encounters[1], encounter1)

    def test_combat_session_creation(self):
        """Test that a combat session can be created"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        self.assertIsInstance(combat_session, CombatSession)
        self.assertEqual(combat_session.encounter, self.encounter)
        self.assertEqual(combat_session.current_round, 1)
        self.assertEqual(combat_session.current_turn_index, 0)
        self.assertTrue(combat_session.is_active)

    def test_combat_session_str_representation(self):
        """Test the string representation of CombatSession"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        expected = (
            f"Combat: {self.encounter.name} - Round {combat_session.current_round}"
        )
        self.assertEqual(str(combat_session), expected)

    def test_combat_session_ordering(self):
        """Test that combat sessions are ordered by started_at descending"""
        # Create different encounters for each session since CombatSession has OneToOneField with Encounter
        encounter1 = EncounterFactory(campaign=self.campaign)
        encounter2 = EncounterFactory(campaign=self.campaign)

        session1 = CombatSessionFactory(encounter=encounter1)
        session2 = CombatSessionFactory(encounter=encounter2)

        sessions = CombatSession.objects.all()
        # Most recent first
        self.assertEqual(sessions[0], session2)
        self.assertEqual(sessions[1], session1)

    def test_combat_participant_player_creation(self):
        """Test that a combat participant can be created for a player"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session,
            participant_type="player",
            player=self.player,
            monster=None,
            initiative=15,
            current_hp=50,
            max_hp=50,
        )

        self.assertIsInstance(participant, CombatParticipant)
        self.assertEqual(participant.combat_session, combat_session)
        self.assertEqual(participant.participant_type, "player")
        self.assertEqual(participant.player, self.player)
        self.assertIsNone(participant.monster)
        self.assertEqual(participant.initiative, 15)
        self.assertEqual(participant.current_hp, 50)
        self.assertEqual(participant.max_hp, 50)
        self.assertFalse(participant.is_dead)
        self.assertFalse(participant.turn_completed)

    def test_combat_participant_monster_creation(self):
        """Test that a combat participant can be created for a monster"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session,
            participant_type="monster",
            player=None,
            monster=self.monster,
            initiative=12,
            current_hp=30,
            max_hp=30,
        )

        self.assertIsInstance(participant, CombatParticipant)
        self.assertEqual(participant.combat_session, combat_session)
        self.assertEqual(participant.participant_type, "monster")
        self.assertIsNone(participant.player)
        self.assertEqual(participant.monster, self.monster)
        self.assertEqual(participant.initiative, 12)
        self.assertEqual(participant.current_hp, 30)
        self.assertEqual(participant.max_hp, 30)

    def test_combat_participant_str_representation_player(self):
        """Test the string representation of CombatParticipant for player"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session,
            participant_type="player",
            player=self.player,
            initiative=15,
        )
        expected = f"{self.player.character_name} (Initiative: 15)"
        self.assertEqual(str(participant), expected)

    def test_combat_participant_str_representation_monster(self):
        """Test the string representation of CombatParticipant for monster"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session,
            participant_type="monster",
            monster=self.monster,
            initiative=12,
        )
        expected = f"{self.monster.name} (Initiative: 12)"
        self.assertEqual(str(participant), expected)

    def test_combat_participant_name_property_player(self):
        """Test the name property for player participant"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session, participant_type="player", player=self.player
        )
        self.assertEqual(participant.name, self.player.character_name)

    def test_combat_participant_name_property_monster(self):
        """Test the name property for monster participant"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session,
            participant_type="monster",
            monster=self.monster,
        )
        self.assertEqual(participant.name, self.monster.name)

    def test_combat_participant_ac_property_player(self):
        """Test the AC property for player participant"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session, participant_type="player", player=self.player
        )
        self.assertEqual(participant.ac, self.player.ac)

    def test_combat_participant_ac_property_monster(self):
        """Test the AC property for monster participant"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session,
            participant_type="monster",
            monster=self.monster,
        )
        self.assertEqual(participant.ac, self.monster.ac)

    def test_combat_participant_ordering(self):
        """Test that combat participants are ordered by initiative descending"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant1 = CombatParticipantFactory(
            combat_session=combat_session, participant_type="player", initiative=10
        )
        participant2 = CombatParticipantFactory(
            combat_session=combat_session, participant_type="monster", initiative=15
        )

        participants = CombatParticipant.objects.all()
        # Higher initiative first
        self.assertEqual(participants[0], participant2)
        self.assertEqual(participants[1], participant1)


class CombatTrackerFormTest(TestCase):
    """Test cases for combat_tracker forms"""

    def setUp(self):
        """Set up test data"""
        self.campaign = CampaignFactory()
        self.player = PlayerFactory(campaign=self.campaign)
        self.monster = MonsterFactory()
        self.encounter = EncounterFactory(campaign=self.campaign)
        self.encounter.players.add(self.player)
        self.encounter.monsters.add(self.monster)

    def test_encounter_form_valid_data(self):
        """Test EncounterForm with valid data"""
        form_data = {
            "name": "Test Encounter",
            "description": "Test description",
            "campaign": self.campaign.pk,
            "players": [self.player.pk],
            "monsters": [self.monster.pk],
        }
        form = EncounterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_encounter_form_required_fields(self):
        """Test that required fields are validated"""
        form_data = {
            "name": "",
            "description": "Test description",
            "campaign": "",
            "players": [],
            "monsters": [],
        }
        form = EncounterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("campaign", form.errors)
        self.assertIn("players", form.errors)
        self.assertIn("monsters", form.errors)

    def test_encounter_form_save(self):
        """Test that EncounterForm can save an encounter"""
        form_data = {
            "name": "Test Encounter",
            "description": "Test description",
            "campaign": self.campaign.pk,
            "players": [self.player.pk],
            "monsters": [self.monster.pk],
        }
        form = EncounterForm(data=form_data)
        self.assertTrue(form.is_valid())

        encounter = form.save()
        self.assertEqual(encounter.name, "Test Encounter")
        self.assertEqual(encounter.description, "Test description")
        self.assertEqual(encounter.campaign, self.campaign)
        self.assertIn(self.player, encounter.players.all())
        self.assertIn(self.monster, encounter.monsters.all())

    def test_initiative_form_creation(self):
        """Test that InitiativeForm is created with correct fields"""
        form = InitiativeForm(self.encounter)

        # Should have fields for each player and monster
        self.assertIn(f"player_{self.player.id}_initiative", form.fields)
        self.assertIn(f"monster_{self.monster.id}_initiative", form.fields)

    def test_initiative_form_valid_data(self):
        """Test InitiativeForm with valid data"""
        # Get all players and monsters from the encounter
        players = list(self.encounter.players.all())
        monsters = list(self.encounter.monsters.all())

        form_data = {}
        for player in players:
            form_data[f"player_{player.id}_initiative"] = 15
        for monster in monsters:
            form_data[f"monster_{monster.id}_initiative"] = 12

        form = InitiativeForm(self.encounter, data=form_data)
        self.assertTrue(form.is_valid())

    def test_initiative_form_invalid_data(self):
        """Test InitiativeForm with invalid data"""
        form_data = {
            f"player_{self.player.id}_initiative": 0,  # Below minimum
            f"monster_{self.monster.id}_initiative": 31,  # Above maximum
        }
        form = InitiativeForm(self.encounter, data=form_data)
        self.assertFalse(form.is_valid())

    def test_hp_tracking_form_valid_data(self):
        """Test HPTrackingForm with valid data"""
        form_data = {"change_type": "damage", "amount": 10, "notes": "Fireball"}
        form = HPTrackingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_hp_tracking_form_required_fields(self):
        """Test that required fields are validated"""
        form_data = {"change_type": "", "amount": "", "notes": ""}
        form = HPTrackingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("change_type", form.errors)
        self.assertIn("amount", form.errors)

    def test_hp_tracking_form_optional_notes(self):
        """Test that notes field is optional"""
        form_data = {"change_type": "healing", "amount": 5}
        form = HPTrackingForm(data=form_data)
        self.assertTrue(form.is_valid())


class CombatTrackerViewTest(TestCase):
    """Test cases for combat_tracker views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = UserFactory()
        self.campaign = CampaignFactory()
        self.player = PlayerFactory(campaign=self.campaign)
        self.monster = MonsterFactory()
        self.encounter = EncounterFactory(campaign=self.campaign)
        self.encounter.players.add(self.player)
        self.encounter.monsters.add(self.monster)

    def test_encounter_list_view_requires_login(self):
        """Test that encounter list view requires login"""
        response = self.client.get(reverse("combat_tracker:encounter_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_encounter_list_view_with_login(self):
        """Test encounter list view with authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("combat_tracker:encounter_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.encounter.name)

    def test_encounter_list_view_search(self):
        """Test encounter list view search functionality"""
        self.client.force_login(self.user)

        # Test search by name
        response = self.client.get(
            reverse("combat_tracker:encounter_list"), {"search": self.encounter.name}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.encounter.name)

        # Test search by campaign title
        response = self.client.get(
            reverse("combat_tracker:encounter_list"), {"search": self.campaign.title}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.encounter.name)

    def test_encounter_detail_view_requires_login(self):
        """Test that encounter detail view requires login"""
        response = self.client.get(
            reverse("combat_tracker:encounter_detail", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_encounter_detail_view_with_login(self):
        """Test encounter detail view with authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("combat_tracker:encounter_detail", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.encounter.name)
        self.assertContains(response, self.player.character_name)
        self.assertContains(response, self.monster.name)

    def test_encounter_create_view_requires_login(self):
        """Test that encounter create view requires login"""
        response = self.client.get(reverse("combat_tracker:encounter_create"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_encounter_create_view_get(self):
        """Test encounter create view GET request"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("combat_tracker:encounter_create"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], EncounterForm)

    def test_encounter_create_view_post_valid(self):
        """Test encounter create view POST with valid data"""
        self.client.force_login(self.user)
        form_data = {
            "name": "New Encounter",
            "description": "New description",
            "campaign": self.campaign.pk,
            "players": [self.player.pk],
            "monsters": [self.monster.pk],
        }
        response = self.client.post(
            reverse("combat_tracker:encounter_create"), form_data
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful creation

        # Check that encounter was created
        self.assertTrue(Encounter.objects.filter(name="New Encounter").exists())

    def test_encounter_update_view_requires_login(self):
        """Test that encounter update view requires login"""
        response = self.client.get(
            reverse("combat_tracker:encounter_update", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_encounter_update_view_get(self):
        """Test encounter update view GET request"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("combat_tracker:encounter_update", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], EncounterForm)
        self.assertEqual(response.context["encounter"], self.encounter)

    def test_encounter_update_view_post_valid(self):
        """Test encounter update view POST with valid data"""
        self.client.force_login(self.user)
        form_data = {
            "name": "Updated Encounter",
            "description": "Updated description",
            "campaign": self.campaign.pk,
            "players": [self.player.pk],
            "monsters": [self.monster.pk],
        }
        response = self.client.post(
            reverse(
                "combat_tracker:encounter_update", kwargs={"pk": self.encounter.pk}
            ),
            form_data,
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful update

        # Check that encounter was updated
        updated_encounter = Encounter.objects.get(pk=self.encounter.pk)
        self.assertEqual(updated_encounter.name, "Updated Encounter")

    def test_encounter_delete_view_requires_login(self):
        """Test that encounter delete view requires login"""
        response = self.client.get(
            reverse("combat_tracker:encounter_delete", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_encounter_delete_view_get(self):
        """Test encounter delete view GET request"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("combat_tracker:encounter_delete", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["encounter"], self.encounter)

    def test_encounter_delete_view_post(self):
        """Test encounter delete view POST request"""
        self.client.force_login(self.user)
        encounter_pk = self.encounter.pk
        response = self.client.post(
            reverse("combat_tracker:encounter_delete", kwargs={"pk": encounter_pk})
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful deletion

        # Check that encounter was deleted
        self.assertFalse(Encounter.objects.filter(pk=encounter_pk).exists())

    def test_start_encounter_view_requires_login(self):
        """Test that start encounter view requires login"""
        response = self.client.get(
            reverse("combat_tracker:start_encounter", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_start_encounter_view_get(self):
        """Test start encounter view GET request"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("combat_tracker:start_encounter", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], InitiativeForm)
        self.assertEqual(response.context["encounter"], self.encounter)

    def test_start_encounter_view_post_valid(self):
        """Test start encounter view POST with valid data"""
        self.client.force_login(self.user)

        # Get all players and monsters from the encounter
        players = list(self.encounter.players.all())
        monsters = list(self.encounter.monsters.all())

        form_data = {}
        for player in players:
            form_data[f"player_{player.id}_initiative"] = 15
        for monster in monsters:
            form_data[f"monster_{monster.id}_initiative"] = 12

        response = self.client.post(
            reverse("combat_tracker:start_encounter", kwargs={"pk": self.encounter.pk}),
            form_data,
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful creation

        # Check that combat session was created
        self.assertTrue(CombatSession.objects.filter(encounter=self.encounter).exists())

        # Check that combat participants were created
        combat_session = CombatSession.objects.get(encounter=self.encounter)
        self.assertTrue(
            CombatParticipant.objects.filter(combat_session=combat_session).exists()
        )

    def test_combat_interface_view_requires_login(self):
        """Test that combat interface view requires login"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        response = self.client.get(
            reverse("combat_tracker:combat_interface", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_combat_interface_view_with_login(self):
        """Test combat interface view with authenticated user"""
        self.client.force_login(self.user)
        combat_session = CombatSessionFactory(encounter=self.encounter)
        CombatParticipantFactory(
            combat_session=combat_session, participant_type="player", player=self.player
        )

        response = self.client.get(
            reverse("combat_tracker:combat_interface", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["encounter"], self.encounter)
        self.assertEqual(response.context["combat_session"], combat_session)

    def test_next_turn_view_requires_login(self):
        """Test that next turn view requires login"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        response = self.client.get(
            reverse("combat_tracker:next_turn", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_next_turn_view_with_login(self):
        """Test next turn view with authenticated user"""
        self.client.force_login(self.user)
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session, participant_type="player", player=self.player
        )

        response = self.client.get(
            reverse("combat_tracker:next_turn", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect after turn advancement

        # Check that combat session was updated (round incremented, turn index reset)
        updated_session = CombatSession.objects.get(pk=combat_session.pk)
        self.assertEqual(
            updated_session.current_round, 2
        )  # Should be round 2 after completing round 1
        self.assertEqual(
            updated_session.current_turn_index, 0
        )  # Should reset to 0 for new round

    def test_end_combat_view_requires_login(self):
        """Test that end combat view requires login"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        response = self.client.get(
            reverse("combat_tracker:end_combat", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_end_combat_view_get(self):
        """Test end combat view GET request"""
        self.client.force_login(self.user)
        combat_session = CombatSessionFactory(encounter=self.encounter)

        response = self.client.get(
            reverse("combat_tracker:end_combat", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["encounter"], self.encounter)
        self.assertEqual(response.context["combat_session"], combat_session)

    def test_end_combat_view_post(self):
        """Test end combat view POST request"""
        self.client.force_login(self.user)
        combat_session = CombatSessionFactory(encounter=self.encounter)

        response = self.client.post(
            reverse("combat_tracker:end_combat", kwargs={"pk": self.encounter.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect after ending combat

        # Check that combat session was marked as inactive
        updated_session = CombatSession.objects.get(pk=combat_session.pk)
        self.assertFalse(updated_session.is_active)

    def test_update_hp_view_requires_login(self):
        """Test that update HP view requires login"""
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(combat_session=combat_session)

        response = self.client.get(
            reverse(
                "combat_tracker:update_hp",
                kwargs={"pk": self.encounter.pk, "participant_id": participant.pk},
            )
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_update_hp_view_get(self):
        """Test update HP view GET request"""
        self.client.force_login(self.user)
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(combat_session=combat_session)

        response = self.client.get(
            reverse(
                "combat_tracker:update_hp",
                kwargs={"pk": self.encounter.pk, "participant_id": participant.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], HPTrackingForm)
        self.assertEqual(response.context["participant"], participant)

    def test_update_hp_view_post_damage(self):
        """Test update HP view POST with damage"""
        self.client.force_login(self.user)
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session, current_hp=50, max_hp=50
        )

        form_data = {"change_type": "damage", "amount": 20, "notes": "Fireball"}
        response = self.client.post(
            reverse(
                "combat_tracker:update_hp",
                kwargs={"pk": self.encounter.pk, "participant_id": participant.pk},
            ),
            form_data,
        )
        self.assertEqual(response.status_code, 302)  # Redirect after HP update

        # Check that HP was reduced
        updated_participant = CombatParticipant.objects.get(pk=participant.pk)
        self.assertEqual(updated_participant.current_hp, 30)

    def test_update_hp_view_post_healing(self):
        """Test update HP view POST with healing"""
        self.client.force_login(self.user)
        combat_session = CombatSessionFactory(encounter=self.encounter)
        participant = CombatParticipantFactory(
            combat_session=combat_session, current_hp=30, max_hp=50
        )

        form_data = {"change_type": "healing", "amount": 15, "notes": "Cure Wounds"}
        response = self.client.post(
            reverse(
                "combat_tracker:update_hp",
                kwargs={"pk": self.encounter.pk, "participant_id": participant.pk},
            ),
            form_data,
        )
        self.assertEqual(response.status_code, 302)  # Redirect after HP update

        # Check that HP was increased
        updated_participant = CombatParticipant.objects.get(pk=participant.pk)
        self.assertEqual(updated_participant.current_hp, 45)


class CombatTrackerUtilityTest(TestCase):
    """Test cases for combat_tracker utility functions"""

    def test_parse_monster_hp_numeric(self):
        """Test parsing numeric HP string"""
        hp_string = "82"
        result = parse_monster_hp(hp_string)
        self.assertEqual(result, 82)

    def test_parse_monster_hp_with_dice(self):
        """Test parsing HP string with dice notation"""
        hp_string = "82 (10d11 + 26)"
        result = parse_monster_hp(hp_string)
        self.assertEqual(result, 82)

    def test_parse_monster_hp_empty(self):
        """Test parsing empty HP string"""
        hp_string = ""
        result = parse_monster_hp(hp_string)
        self.assertEqual(result, 0)

    def test_parse_monster_hp_none(self):
        """Test parsing None HP"""
        hp_string = None
        result = parse_monster_hp(hp_string)
        self.assertEqual(result, 0)

    def test_parse_monster_hp_invalid(self):
        """Test parsing invalid HP string"""
        hp_string = "invalid"
        result = parse_monster_hp(hp_string)
        self.assertEqual(result, 0)
