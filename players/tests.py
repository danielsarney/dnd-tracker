from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from dnd_tracker.factories import (
    UserFactory,
    CampaignFactory,
    PlayerFactory,
)
from players.models import Player
from players.forms import PlayerForm

User = get_user_model()


class PlayerModelTest(TestCase):
    """Test cases for the Player model"""

    def setUp(self):
        """Set up test data"""
        self.campaign = CampaignFactory()
        self.player = PlayerFactory(campaign=self.campaign)

    def test_player_creation(self):
        """Test that a player can be created with all required fields"""
        self.assertIsInstance(self.player, Player)
        self.assertEqual(self.player.campaign, self.campaign)
        self.assertIsNotNone(self.player.character_name)
        self.assertIsNotNone(self.player.player_name)
        self.assertIsNotNone(self.player.character_class)
        self.assertIsNotNone(self.player.race)
        self.assertIsNotNone(self.player.level)
        self.assertIsNotNone(self.player.ac)
        self.assertIsNotNone(self.player.background)

    def test_player_string_representation(self):
        """Test the string representation of a player"""
        expected_str = f"{self.player.character_name} ({self.player.player_name})"
        self.assertEqual(str(self.player), expected_str)

    def test_player_ordering(self):
        """Test that players are ordered by character_name"""
        player1 = PlayerFactory(campaign=self.campaign, character_name="Zelda")
        player2 = PlayerFactory(campaign=self.campaign, character_name="Alice")
        player3 = PlayerFactory(campaign=self.campaign, character_name="Bob")

        players = Player.objects.all()
        character_names = [p.character_name for p in players]

        # Should be ordered alphabetically by character_name
        self.assertEqual(character_names, sorted(character_names))

    def test_player_campaign_relationship(self):
        """Test the relationship between Player and Campaign"""
        self.assertEqual(self.player.campaign, self.campaign)
        self.assertIn(self.player, self.campaign.players.all())

    def test_player_subclass_optional(self):
        """Test that subclass field is optional"""
        player_without_subclass = PlayerFactory(campaign=self.campaign, subclass=None)
        self.assertIsNone(player_without_subclass.subclass)

        player_with_subclass = PlayerFactory(
            campaign=self.campaign, subclass="Champion"
        )
        self.assertEqual(player_with_subclass.subclass, "Champion")

    def test_player_level_default(self):
        """Test that level defaults to 1"""
        player = PlayerFactory(campaign=self.campaign)
        self.assertGreaterEqual(player.level, 1)

    def test_player_ac_positive(self):
        """Test that AC is a positive integer"""
        player = PlayerFactory(campaign=self.campaign)
        self.assertGreater(player.ac, 0)

    def test_player_cascade_delete(self):
        """Test that players are deleted when campaign is deleted"""
        campaign = CampaignFactory()
        player = PlayerFactory(campaign=campaign)
        player_id = player.id

        campaign.delete()

        with self.assertRaises(Player.DoesNotExist):
            Player.objects.get(id=player_id)


class PlayerFormTest(TestCase):
    """Test cases for the PlayerForm"""

    def setUp(self):
        """Set up test data"""
        self.campaign = CampaignFactory()
        self.form_data = {
            "character_name": "Test Character",
            "player_name": "Test Player",
            "character_class": "Wizard",
            "subclass": "Evocation",
            "race": "Human",
            "level": 5,
            "ac": 15,
            "background": "A mysterious wizard from the north",
            "campaign": self.campaign.id,
        }

    def test_valid_form(self):
        """Test form with valid data"""
        form = PlayerForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_save(self):
        """Test that form can save a player"""
        form = PlayerForm(data=self.form_data)
        self.assertTrue(form.is_valid())

        player = form.save()
        self.assertIsInstance(player, Player)
        self.assertEqual(player.character_name, "Test Character")
        self.assertEqual(player.player_name, "Test Player")
        self.assertEqual(player.character_class, "Wizard")
        self.assertEqual(player.subclass, "Evocation")
        self.assertEqual(player.race, "Human")
        self.assertEqual(player.level, 5)
        self.assertEqual(player.ac, 15)
        self.assertEqual(player.background, "A mysterious wizard from the north")
        self.assertEqual(player.campaign, self.campaign)

    def test_form_without_subclass(self):
        """Test form without subclass (optional field)"""
        form_data = self.form_data.copy()
        form_data["subclass"] = ""

        form = PlayerForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """Test form validation with missing required fields"""
        required_fields = [
            "character_name",
            "player_name",
            "character_class",
            "race",
            "level",
            "ac",
            "background",
            "campaign",
        ]

        for field in required_fields:
            form_data = self.form_data.copy()
            del form_data[field]

            form = PlayerForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_form_field_requirements(self):
        """Test that form fields have correct requirements"""
        form = PlayerForm()

        # Required fields
        self.assertTrue(form.fields["character_name"].required)
        self.assertTrue(form.fields["player_name"].required)
        self.assertTrue(form.fields["character_class"].required)
        self.assertTrue(form.fields["race"].required)
        self.assertTrue(form.fields["level"].required)
        self.assertTrue(form.fields["ac"].required)
        self.assertTrue(form.fields["background"].required)
        self.assertTrue(form.fields["campaign"].required)

        # Optional fields
        self.assertFalse(form.fields["subclass"].required)

    def test_form_widgets(self):
        """Test that form widgets are configured correctly"""
        form = PlayerForm()

        # Check that widgets have correct CSS classes
        self.assertIn("form-control", str(form.fields["character_name"].widget.attrs))
        self.assertIn("form-control", str(form.fields["player_name"].widget.attrs))
        self.assertIn("form-control", str(form.fields["character_class"].widget.attrs))
        self.assertIn("form-control", str(form.fields["subclass"].widget.attrs))
        self.assertIn("form-control", str(form.fields["race"].widget.attrs))
        self.assertIn("form-control", str(form.fields["level"].widget.attrs))
        self.assertIn("form-control", str(form.fields["ac"].widget.attrs))
        self.assertIn("form-control", str(form.fields["background"].widget.attrs))
        self.assertIn("form-control", str(form.fields["campaign"].widget.attrs))


class PlayerViewTest(TestCase):
    """Test cases for Player views"""

    def setUp(self):
        """Set up test data"""
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user)

        self.campaign = CampaignFactory()
        self.player = PlayerFactory(campaign=self.campaign)

    def test_player_list_view_authenticated(self):
        """Test player list view for authenticated user"""
        response = self.client.get(reverse("players:player_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.character_name)
        self.assertContains(response, self.player.player_name)

    def test_player_list_view_unauthenticated(self):
        """Test player list view redirects for unauthenticated user"""
        self.client.logout()
        response = self.client.get(reverse("players:player_list"))
        self.assertEqual(response.status_code, 302)

    def test_player_list_view_search(self):
        """Test player list view with search functionality"""
        # Create additional players for search testing
        PlayerFactory(campaign=self.campaign, character_name="Gandalf")
        PlayerFactory(campaign=self.campaign, character_name="Aragorn")

        # Search by character name
        response = self.client.get(
            reverse("players:player_list"), {"search": "Gandalf"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gandalf")
        self.assertNotContains(response, "Aragorn")

        # Search by player name
        response = self.client.get(
            reverse("players:player_list"), {"search": self.player.player_name}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.character_name)

        # Search by character class
        response = self.client.get(
            reverse("players:player_list"), {"search": self.player.character_class}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.character_name)

        # Search by race
        response = self.client.get(
            reverse("players:player_list"), {"search": self.player.race}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.character_name)

        # Search by campaign title
        response = self.client.get(
            reverse("players:player_list"), {"search": self.campaign.title}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.character_name)

    def test_player_detail_view_authenticated(self):
        """Test player detail view for authenticated user"""
        response = self.client.get(
            reverse("players:player_detail", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.character_name)
        self.assertContains(response, self.player.player_name)
        self.assertContains(response, self.player.character_class)
        self.assertContains(response, self.player.race)
        self.assertContains(response, self.player.background)

    def test_player_detail_view_unauthenticated(self):
        """Test player detail view redirects for unauthenticated user"""
        self.client.logout()
        response = self.client.get(
            reverse("players:player_detail", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_player_detail_view_not_found(self):
        """Test player detail view with non-existent player"""
        response = self.client.get(
            reverse("players:player_detail", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)

    def test_player_create_view_get(self):
        """Test player create view GET request"""
        response = self.client.get(reverse("players:player_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_player_create_view_post_valid(self):
        """Test player create view POST with valid data"""
        form_data = {
            "character_name": "New Character",
            "player_name": "New Player",
            "character_class": "Rogue",
            "subclass": "Assassin",
            "race": "Elf",
            "level": 3,
            "ac": 14,
            "background": "A stealthy elf rogue",
            "campaign": self.campaign.id,
        }

        response = self.client.post(reverse("players:player_create"), form_data)
        self.assertEqual(response.status_code, 302)

        # Check that player was created
        new_player = Player.objects.get(character_name="New Character")
        self.assertEqual(new_player.player_name, "New Player")
        self.assertEqual(new_player.character_class, "Rogue")
        self.assertEqual(new_player.campaign, self.campaign)

    def test_player_create_view_post_invalid(self):
        """Test player create view POST with invalid data"""
        form_data = {
            "character_name": "",  # Invalid: required field empty
            "player_name": "New Player",
            "character_class": "Rogue",
            "race": "Elf",
            "level": 3,
            "ac": 14,
            "background": "A stealthy elf rogue",
            "campaign": self.campaign.id,
        }

        response = self.client.post(reverse("players:player_create"), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
        self.assertContains(response, "error")

    def test_player_create_view_unauthenticated(self):
        """Test player create view redirects for unauthenticated user"""
        self.client.logout()
        response = self.client.get(reverse("players:player_create"))
        self.assertEqual(response.status_code, 302)

    def test_player_update_view_get(self):
        """Test player update view GET request"""
        response = self.client.get(
            reverse("players:player_update", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
        self.assertContains(response, self.player.character_name)

    def test_player_update_view_post_valid(self):
        """Test player update view POST with valid data"""
        form_data = {
            "character_name": "Updated Character",
            "player_name": "Updated Player",
            "character_class": "Paladin",
            "subclass": "Devotion",
            "race": "Human",
            "level": 7,
            "ac": 18,
            "background": "A noble paladin",
            "campaign": self.campaign.id,
        }

        response = self.client.post(
            reverse("players:player_update", kwargs={"pk": self.player.pk}), form_data
        )
        self.assertEqual(response.status_code, 302)

        # Check that player was updated
        updated_player = Player.objects.get(pk=self.player.pk)
        self.assertEqual(updated_player.character_name, "Updated Character")
        self.assertEqual(updated_player.player_name, "Updated Player")
        self.assertEqual(updated_player.character_class, "Paladin")

    def test_player_update_view_post_invalid(self):
        """Test player update view POST with invalid data"""
        form_data = {
            "character_name": "",  # Invalid: required field empty
            "player_name": "Updated Player",
            "character_class": "Paladin",
            "race": "Human",
            "level": 7,
            "ac": 18,
            "background": "A noble paladin",
            "campaign": self.campaign.id,
        }

        response = self.client.post(
            reverse("players:player_update", kwargs={"pk": self.player.pk}), form_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_player_update_view_unauthenticated(self):
        """Test player update view redirects for unauthenticated user"""
        self.client.logout()
        response = self.client.get(
            reverse("players:player_update", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_player_delete_view_get(self):
        """Test player delete view GET request"""
        response = self.client.get(
            reverse("players:player_delete", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.character_name)
        self.assertContains(response, "delete")

    def test_player_delete_view_post(self):
        """Test player delete view POST request"""
        player_id = self.player.pk

        response = self.client.post(
            reverse("players:player_delete", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 302)

        # Check that player was deleted
        with self.assertRaises(Player.DoesNotExist):
            Player.objects.get(pk=player_id)

    def test_player_delete_view_unauthenticated(self):
        """Test player delete view redirects for unauthenticated user"""
        self.client.logout()
        response = self.client.get(
            reverse("players:player_delete", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 302)


class PlayerURLTest(TestCase):
    """Test cases for Player URL patterns"""

    def setUp(self):
        """Set up test data"""
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user)

        self.campaign = CampaignFactory()
        self.player = PlayerFactory(campaign=self.campaign)

    def test_player_list_url(self):
        """Test player list URL"""
        response = self.client.get(reverse("players:player_list"))
        self.assertEqual(response.status_code, 200)

    def test_player_detail_url(self):
        """Test player detail URL"""
        response = self.client.get(
            reverse("players:player_detail", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_player_create_url(self):
        """Test player create URL"""
        response = self.client.get(reverse("players:player_create"))
        self.assertEqual(response.status_code, 200)

    def test_player_update_url(self):
        """Test player update URL"""
        response = self.client.get(
            reverse("players:player_update", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_player_delete_url(self):
        """Test player delete URL"""
        response = self.client.get(
            reverse("players:player_delete", kwargs={"pk": self.player.pk})
        )
        self.assertEqual(response.status_code, 200)


class PlayerIntegrationTest(TestCase):
    """Integration tests for Player functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user)

        self.campaign = CampaignFactory()

    def test_complete_player_lifecycle(self):
        """Test complete CRUD lifecycle for a player"""
        # Create
        form_data = {
            "character_name": "Test Character",
            "player_name": "Test Player",
            "character_class": "Wizard",
            "subclass": "Evocation",
            "race": "Human",
            "level": 5,
            "ac": 15,
            "background": "A powerful wizard",
            "campaign": self.campaign.id,
        }

        response = self.client.post(reverse("players:player_create"), form_data)
        self.assertEqual(response.status_code, 302)

        # Read
        player = Player.objects.get(character_name="Test Character")
        self.assertEqual(player.player_name, "Test Player")

        # Update
        update_data = form_data.copy()
        update_data["level"] = 6
        update_data["ac"] = 16

        response = self.client.post(
            reverse("players:player_update", kwargs={"pk": player.pk}), update_data
        )
        self.assertEqual(response.status_code, 302)

        updated_player = Player.objects.get(pk=player.pk)
        self.assertEqual(updated_player.level, 6)
        self.assertEqual(updated_player.ac, 16)

        # Delete
        response = self.client.post(
            reverse("players:player_delete", kwargs={"pk": player.pk})
        )
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(Player.DoesNotExist):
            Player.objects.get(pk=player.pk)

    def test_multiple_players_same_campaign(self):
        """Test creating multiple players for the same campaign"""
        players_data = [
            {
                "character_name": "Character 1",
                "player_name": "Player 1",
                "character_class": "Fighter",
                "race": "Human",
                "level": 1,
                "ac": 16,
                "background": "A brave fighter",
                "campaign": self.campaign.id,
            },
            {
                "character_name": "Character 2",
                "player_name": "Player 2",
                "character_class": "Wizard",
                "race": "Elf",
                "level": 1,
                "ac": 12,
                "background": "A wise wizard",
                "campaign": self.campaign.id,
            },
        ]

        for player_data in players_data:
            response = self.client.post(reverse("players:player_create"), player_data)
            self.assertEqual(response.status_code, 302)

        # Verify both players exist and belong to the same campaign
        players = Player.objects.filter(campaign=self.campaign)
        self.assertEqual(players.count(), 2)

        character_names = [p.character_name for p in players]
        self.assertIn("Character 1", character_names)
        self.assertIn("Character 2", character_names)

    def test_player_search_functionality(self):
        """Test comprehensive search functionality"""
        # Create players with different characteristics
        PlayerFactory(
            campaign=self.campaign,
            character_name="Gandalf",
            player_name="John",
            character_class="Wizard",
            race="Human",
        )
        PlayerFactory(
            campaign=self.campaign,
            character_name="Legolas",
            player_name="Jane",
            character_class="Ranger",
            race="Elf",
        )
        PlayerFactory(
            campaign=self.campaign,
            character_name="Gimli",
            player_name="Bob",
            character_class="Fighter",
            race="Dwarf",
        )

        # Test various search queries
        search_tests = [
            ("Gandalf", ["Gandalf"]),
            ("John", ["Gandalf"]),
            ("Wizard", ["Gandalf"]),
            ("Elf", ["Legolas"]),
            ("Fighter", ["Gimli"]),
            ("G", ["Gandalf", "Gimli"]),  # Should match both Gandalf and Gimli
        ]

        for search_term, expected_characters in search_tests:
            response = self.client.get(
                reverse("players:player_list"), {"search": search_term}
            )
            self.assertEqual(response.status_code, 200)

            for character in expected_characters:
                self.assertContains(response, character)
