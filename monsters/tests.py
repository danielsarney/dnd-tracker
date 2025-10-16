from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from dnd_tracker.factories import (
    UserFactory,
    MonsterFactory,
)
from monsters.models import Monster
from monsters.forms import MonsterForm

User = get_user_model()


class MonsterModelTest(TestCase):
    """Test cases for the Monster model"""

    def setUp(self):
        """Set up test data"""
        self.monster = MonsterFactory()

    def test_monster_creation(self):
        """Test that a monster can be created with all required fields"""
        self.assertIsInstance(self.monster, Monster)
        self.assertIsNotNone(self.monster.name)
        self.assertIsNotNone(self.monster.ac)
        self.assertIsNotNone(self.monster.initiative)
        self.assertIsNotNone(self.monster.hp)
        self.assertIsNotNone(self.monster.speed)
        self.assertIsNotNone(self.monster.challenge_rating)

    def test_monster_string_representation(self):
        """Test the string representation of a monster"""
        self.assertEqual(str(self.monster), self.monster.name)

    def test_monster_ordering(self):
        """Test that monsters are ordered by name"""
        monster1 = MonsterFactory(name="Zombie")
        monster2 = MonsterFactory(name="Ancient Dragon")
        monster3 = MonsterFactory(name="Goblin")

        monsters = Monster.objects.all()
        monster_names = [m.name for m in monsters]

        # Should be ordered alphabetically by name
        self.assertEqual(monster_names, sorted(monster_names))

    def test_monster_ability_scores(self):
        """Test monster ability score fields"""
        monster = MonsterFactory()

        # Test all ability score fields exist and have default values
        ability_fields = [
            "strength",
            "strength_mod",
            "strength_save",
            "dexterity",
            "dexterity_mod",
            "dexterity_save",
            "constitution",
            "constitution_mod",
            "constitution_save",
            "intelligence",
            "intelligence_mod",
            "intelligence_save",
            "wisdom",
            "wisdom_mod",
            "wisdom_save",
            "charisma",
            "charisma_mod",
            "charisma_save",
        ]

        for field in ability_fields:
            self.assertIsNotNone(getattr(monster, field))

    def test_monster_optional_fields(self):
        """Test that optional fields can be null or empty"""
        monster = MonsterFactory(
            skills=None,
            resistances=None,
            immunities=None,
            vulnerabilities=None,
            senses=None,
            languages=None,
            gear=None,
            traits=None,
            actions=None,
            bonus_actions=None,
            reactions=None,
            legendary_actions=None,
        )

        optional_fields = [
            "skills",
            "resistances",
            "immunities",
            "vulnerabilities",
            "senses",
            "languages",
            "gear",
            "traits",
            "actions",
            "bonus_actions",
            "reactions",
            "legendary_actions",
        ]

        for field in optional_fields:
            self.assertIsNone(getattr(monster, field))

    def test_monster_ac_positive(self):
        """Test that AC is a positive integer"""
        monster = MonsterFactory()
        self.assertGreater(monster.ac, 0)

    def test_monster_default_values(self):
        """Test that modifier and save fields have default values"""
        monster = MonsterFactory()

        # Test default values for modifiers and saves
        default_fields = [
            "strength_mod",
            "strength_save",
            "dexterity_mod",
            "dexterity_save",
            "constitution_mod",
            "constitution_save",
            "intelligence_mod",
            "intelligence_save",
            "wisdom_mod",
            "wisdom_save",
            "charisma_mod",
            "charisma_save",
        ]

        for field in default_fields:
            value = getattr(monster, field)
            self.assertIsNotNone(value)
            self.assertIn("+", value)  # Should contain a modifier like "+0"

    def test_monster_field_lengths(self):
        """Test that field length constraints are respected"""
        monster = MonsterFactory()

        # Test that string fields don't exceed their max_length
        self.assertLessEqual(len(monster.name), 200)
        self.assertLessEqual(len(monster.initiative), 50)
        self.assertLessEqual(len(monster.hp), 100)
        self.assertLessEqual(len(monster.speed), 200)
        self.assertLessEqual(len(monster.challenge_rating), 20)


class MonsterFormTest(TestCase):
    """Test cases for the MonsterForm"""

    def setUp(self):
        """Set up test data"""
        self.form_data = {
            "name": "Test Dragon",
            "ac": 20,
            "initiative": "+5",
            "hp": "200 (20d10 + 90)",
            "speed": "40 ft, fly 80 ft",
            "strength": "24",
            "strength_mod": "+7",
            "strength_save": "+7",
            "dexterity": "19",
            "dexterity_mod": "+4",
            "dexterity_save": "+4",
            "constitution": "22",
            "constitution_mod": "+6",
            "constitution_save": "+6",
            "intelligence": "18",
            "intelligence_mod": "+4",
            "intelligence_save": "+4",
            "wisdom": "16",
            "wisdom_mod": "+3",
            "wisdom_save": "+3",
            "charisma": "20",
            "charisma_mod": "+5",
            "charisma_save": "+5",
            "skills": "Athletics +13, Perception +9",
            "resistances": "Fire, Cold, Lightning",
            "immunities": "Poison, Charmed",
            "vulnerabilities": "None",
            "senses": "Darkvision 120 ft",
            "languages": "Common, Draconic",
            "gear": "Greatsword, Plate Armor",
            "challenge_rating": "CR 15",
            "traits": "Magic Resistance",
            "actions": "Multiattack. The dragon makes three attacks.",
            "bonus_actions": "Quick Strike",
            "reactions": "Parry",
            "legendary_actions": "The dragon can take 3 legendary actions.",
        }

    def test_valid_form(self):
        """Test form with valid data"""
        form = MonsterForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_save(self):
        """Test that form can save a monster"""
        form = MonsterForm(data=self.form_data)
        self.assertTrue(form.is_valid())

        monster = form.save()
        self.assertIsInstance(monster, Monster)
        self.assertEqual(monster.name, "Test Dragon")
        self.assertEqual(monster.ac, 20)
        self.assertEqual(monster.initiative, "+5")
        self.assertEqual(monster.hp, "200 (20d10 + 90)")
        self.assertEqual(monster.speed, "40 ft, fly 80 ft")
        self.assertEqual(monster.strength, "24")
        self.assertEqual(monster.strength_mod, "+7")
        self.assertEqual(monster.challenge_rating, "CR 15")

    def test_form_with_optional_fields_empty(self):
        """Test form with optional fields empty"""
        form_data = self.form_data.copy()
        optional_fields = [
            "skills",
            "resistances",
            "immunities",
            "vulnerabilities",
            "senses",
            "languages",
            "gear",
            "traits",
            "actions",
            "bonus_actions",
            "reactions",
            "legendary_actions",
        ]

        for field in optional_fields:
            form_data[field] = ""

        form = MonsterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """Test form validation with missing required fields"""
        required_fields = [
            "name",
            "ac",
            "initiative",
            "hp",
            "speed",
            "strength",
            "strength_mod",
            "strength_save",
            "dexterity",
            "dexterity_mod",
            "dexterity_save",
            "constitution",
            "constitution_mod",
            "constitution_save",
            "intelligence",
            "intelligence_mod",
            "intelligence_save",
            "wisdom",
            "wisdom_mod",
            "wisdom_save",
            "charisma",
            "charisma_mod",
            "charisma_save",
            "challenge_rating",
        ]

        for field in required_fields:
            form_data = self.form_data.copy()
            del form_data[field]

            form = MonsterForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_form_field_requirements(self):
        """Test that form fields have correct requirements"""
        form = MonsterForm()

        # Required fields
        required_fields = [
            "name",
            "ac",
            "initiative",
            "hp",
            "speed",
            "strength",
            "strength_mod",
            "strength_save",
            "dexterity",
            "dexterity_mod",
            "dexterity_save",
            "constitution",
            "constitution_mod",
            "constitution_save",
            "intelligence",
            "intelligence_mod",
            "intelligence_save",
            "wisdom",
            "wisdom_mod",
            "wisdom_save",
            "charisma",
            "charisma_mod",
            "charisma_save",
            "challenge_rating",
        ]

        for field in required_fields:
            self.assertTrue(form.fields[field].required)

        # Optional fields
        optional_fields = [
            "skills",
            "resistances",
            "immunities",
            "vulnerabilities",
            "senses",
            "languages",
            "gear",
            "traits",
            "actions",
            "bonus_actions",
            "reactions",
            "legendary_actions",
        ]

        for field in optional_fields:
            self.assertFalse(form.fields[field].required)

    def test_form_widgets(self):
        """Test that form widgets are configured correctly"""
        form = MonsterForm()

        # Check that widgets have correct CSS classes
        text_fields = [
            "name",
            "initiative",
            "hp",
            "speed",
            "strength",
            "strength_mod",
            "strength_save",
            "dexterity",
            "dexterity_mod",
            "dexterity_save",
            "constitution",
            "constitution_mod",
            "constitution_save",
            "intelligence",
            "intelligence_mod",
            "intelligence_save",
            "wisdom",
            "wisdom_mod",
            "wisdom_save",
            "charisma",
            "charisma_mod",
            "charisma_save",
            "challenge_rating",
        ]

        for field in text_fields:
            self.assertIn("form-control", str(form.fields[field].widget.attrs))

        # Check number input for AC
        self.assertIn("form-control", str(form.fields["ac"].widget.attrs))

        # Check textarea fields
        textarea_fields = [
            "skills",
            "resistances",
            "immunities",
            "vulnerabilities",
            "senses",
            "languages",
            "gear",
            "traits",
            "actions",
            "bonus_actions",
            "reactions",
            "legendary_actions",
        ]

        for field in textarea_fields:
            self.assertIn("form-control", str(form.fields[field].widget.attrs))


class MonsterViewTest(TestCase):
    """Test cases for Monster views"""

    def setUp(self):
        """Set up test data"""
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user)

        self.monster = MonsterFactory()

    def test_monster_list_view_authenticated(self):
        """Test monster list view for authenticated user"""
        response = self.client.get(reverse("monsters:monster_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monster.name)
        self.assertContains(response, self.monster.challenge_rating)

    def test_monster_list_view_unauthenticated(self):
        """Test monster list view redirects for unauthenticated user"""
        self.client.logout()
        response = self.client.get(reverse("monsters:monster_list"))
        self.assertEqual(response.status_code, 302)

    def test_monster_list_view_search(self):
        """Test monster list view with search functionality"""
        # Create additional monsters for search testing
        MonsterFactory(name="Ancient Dragon", challenge_rating="CR 20")
        MonsterFactory(name="Goblin", challenge_rating="CR 1/4")

        # Search by name
        response = self.client.get(
            reverse("monsters:monster_list"), {"search": "Dragon"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ancient Dragon")
        self.assertNotContains(response, "Goblin")

        # Search by challenge rating
        response = self.client.get(
            reverse("monsters:monster_list"), {"search": "CR 20"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ancient Dragon")

        # Search by traits
        dragon = MonsterFactory(
            name="Fire Dragon", traits="Fire Breath, Immunity to Fire"
        )
        response = self.client.get(
            reverse("monsters:monster_list"), {"search": "Fire Breath"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fire Dragon")

        # Search by actions
        response = self.client.get(
            reverse("monsters:monster_list"), {"search": "Multiattack"}
        )
        self.assertEqual(response.status_code, 200)

    def test_monster_detail_view_authenticated(self):
        """Test monster detail view for authenticated user"""
        response = self.client.get(
            reverse("monsters:monster_detail", kwargs={"pk": self.monster.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monster.name)
        self.assertContains(response, self.monster.ac)
        self.assertContains(response, self.monster.initiative)
        self.assertContains(response, self.monster.hp)
        self.assertContains(response, self.monster.challenge_rating)

    def test_monster_detail_view_unauthenticated(self):
        """Test monster detail view redirects for unauthenticated user"""
        self.client.logout()
        response = self.client.get(
            reverse("monsters:monster_detail", kwargs={"pk": self.monster.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_monster_detail_view_not_found(self):
        """Test monster detail view with non-existent monster"""
        response = self.client.get(
            reverse("monsters:monster_detail", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)

    def test_monster_create_view_get(self):
        """Test monster create view GET request"""
        response = self.client.get(reverse("monsters:monster_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_monster_create_view_post_valid(self):
        """Test monster create view POST with valid data"""
        form_data = {
            "name": "New Dragon",
            "ac": 18,
            "initiative": "+3",
            "hp": "150 (15d10 + 60)",
            "speed": "30 ft, fly 60 ft",
            "strength": "20",
            "strength_mod": "+5",
            "strength_save": "+5",
            "dexterity": "15",
            "dexterity_mod": "+2",
            "dexterity_save": "+2",
            "constitution": "18",
            "constitution_mod": "+4",
            "constitution_save": "+4",
            "intelligence": "14",
            "intelligence_mod": "+2",
            "intelligence_save": "+2",
            "wisdom": "13",
            "wisdom_mod": "+1",
            "wisdom_save": "+1",
            "charisma": "16",
            "charisma_mod": "+3",
            "charisma_save": "+3",
            "skills": "Athletics +8, Perception +4",
            "resistances": "Fire",
            "immunities": "None",
            "vulnerabilities": "Cold",
            "senses": "Darkvision 60 ft",
            "languages": "Common, Draconic",
            "gear": "Claws, Bite",
            "challenge_rating": "CR 8",
            "traits": "Fire Resistance",
            "actions": "Multiattack. The dragon makes two attacks.",
            "bonus_actions": "None",
            "reactions": "None",
            "legendary_actions": "None",
        }

        response = self.client.post(reverse("monsters:monster_create"), form_data)
        self.assertEqual(response.status_code, 302)

        # Check that monster was created
        new_monster = Monster.objects.get(name="New Dragon")
        self.assertEqual(new_monster.ac, 18)
        self.assertEqual(new_monster.initiative, "+3")
        self.assertEqual(new_monster.challenge_rating, "CR 8")

    def test_monster_create_view_post_invalid(self):
        """Test monster create view POST with invalid data"""
        form_data = {
            "name": "",  # Invalid: required field empty
            "ac": 18,
            "initiative": "+3",
            "hp": "150 (15d10 + 60)",
            "speed": "30 ft, fly 60 ft",
            "strength": "20",
            "strength_mod": "+5",
            "strength_save": "+5",
            "dexterity": "15",
            "dexterity_mod": "+2",
            "dexterity_save": "+2",
            "constitution": "18",
            "constitution_mod": "+4",
            "constitution_save": "+4",
            "intelligence": "14",
            "intelligence_mod": "+2",
            "intelligence_save": "+2",
            "wisdom": "13",
            "wisdom_mod": "+1",
            "wisdom_save": "+1",
            "charisma": "16",
            "charisma_mod": "+3",
            "charisma_save": "+3",
            "challenge_rating": "CR 8",
        }

        response = self.client.post(reverse("monsters:monster_create"), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
        self.assertContains(response, "This field is required.")

    def test_monster_create_view_unauthenticated(self):
        """Test monster create view redirects for unauthenticated user"""
        self.client.logout()
        response = self.client.get(reverse("monsters:monster_create"))
        self.assertEqual(response.status_code, 302)

    def test_monster_update_view_get(self):
        """Test monster update view GET request"""
        response = self.client.get(
            reverse("monsters:monster_update", kwargs={"pk": self.monster.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
        self.assertContains(response, self.monster.name)

    def test_monster_update_view_post_valid(self):
        """Test monster update view POST with valid data"""
        form_data = {
            "name": "Updated Dragon",
            "ac": 22,
            "initiative": "+7",
            "hp": "300 (25d10 + 150)",
            "speed": "40 ft, fly 80 ft",
            "strength": "26",
            "strength_mod": "+8",
            "strength_save": "+8",
            "dexterity": "17",
            "dexterity_mod": "+3",
            "dexterity_save": "+3",
            "constitution": "24",
            "constitution_mod": "+7",
            "constitution_save": "+7",
            "intelligence": "20",
            "intelligence_mod": "+5",
            "intelligence_save": "+5",
            "wisdom": "18",
            "wisdom_mod": "+4",
            "wisdom_save": "+4",
            "charisma": "22",
            "charisma_mod": "+6",
            "charisma_save": "+6",
            "skills": "Athletics +15, Perception +11",
            "resistances": "Fire, Cold, Lightning",
            "immunities": "Poison, Charmed, Frightened",
            "vulnerabilities": "None",
            "senses": "Darkvision 120 ft, Blindsight 60 ft",
            "languages": "Common, Draconic, Telepathy 120 ft",
            "gear": "Greatsword +3, Plate Armor +2",
            "challenge_rating": "CR 20",
            "traits": "Magic Resistance, Legendary Resistance (3/day)",
            "actions": "Multiattack. The dragon makes three attacks.",
            "bonus_actions": "Quick Strike",
            "reactions": "Parry",
            "legendary_actions": "The dragon can take 3 legendary actions.",
        }

        response = self.client.post(
            reverse("monsters:monster_update", kwargs={"pk": self.monster.pk}),
            form_data,
        )
        self.assertEqual(response.status_code, 302)

        # Check that monster was updated
        updated_monster = Monster.objects.get(pk=self.monster.pk)
        self.assertEqual(updated_monster.name, "Updated Dragon")
        self.assertEqual(updated_monster.ac, 22)
        self.assertEqual(updated_monster.challenge_rating, "CR 20")

    def test_monster_update_view_post_invalid(self):
        """Test monster update view POST with invalid data"""
        form_data = {
            "name": "",  # Invalid: required field empty
            "ac": 22,
            "initiative": "+7",
            "hp": "300 (25d10 + 150)",
            "speed": "40 ft, fly 80 ft",
            "strength": "26",
            "strength_mod": "+8",
            "strength_save": "+8",
            "dexterity": "17",
            "dexterity_mod": "+3",
            "dexterity_save": "+3",
            "constitution": "24",
            "constitution_mod": "+7",
            "constitution_save": "+7",
            "intelligence": "20",
            "intelligence_mod": "+5",
            "intelligence_save": "+5",
            "wisdom": "18",
            "wisdom_mod": "+4",
            "wisdom_save": "+4",
            "charisma": "22",
            "charisma_mod": "+6",
            "charisma_save": "+6",
            "challenge_rating": "CR 20",
        }

        response = self.client.post(
            reverse("monsters:monster_update", kwargs={"pk": self.monster.pk}),
            form_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_monster_update_view_unauthenticated(self):
        """Test monster update view redirects for unauthenticated user"""
        self.client.logout()
        response = self.client.get(
            reverse("monsters:monster_update", kwargs={"pk": self.monster.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_monster_delete_view_get(self):
        """Test monster delete view GET request"""
        response = self.client.get(
            reverse("monsters:monster_delete", kwargs={"pk": self.monster.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.monster.name)
        self.assertContains(response, "delete")

    def test_monster_delete_view_post(self):
        """Test monster delete view POST request"""
        monster_id = self.monster.pk

        response = self.client.post(
            reverse("monsters:monster_delete", kwargs={"pk": self.monster.pk})
        )
        self.assertEqual(response.status_code, 302)

        # Check that monster was deleted
        with self.assertRaises(Monster.DoesNotExist):
            Monster.objects.get(pk=monster_id)

    def test_monster_delete_view_unauthenticated(self):
        """Test monster delete view redirects for unauthenticated user"""
        self.client.logout()
        response = self.client.get(
            reverse("monsters:monster_delete", kwargs={"pk": self.monster.pk})
        )
        self.assertEqual(response.status_code, 302)


class MonsterURLTest(TestCase):
    """Test cases for Monster URL patterns"""

    def setUp(self):
        """Set up test data"""
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user)

        self.monster = MonsterFactory()

    def test_monster_list_url(self):
        """Test monster list URL"""
        response = self.client.get(reverse("monsters:monster_list"))
        self.assertEqual(response.status_code, 200)

    def test_monster_detail_url(self):
        """Test monster detail URL"""
        response = self.client.get(
            reverse("monsters:monster_detail", kwargs={"pk": self.monster.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_monster_create_url(self):
        """Test monster create URL"""
        response = self.client.get(reverse("monsters:monster_create"))
        self.assertEqual(response.status_code, 200)

    def test_monster_update_url(self):
        """Test monster update URL"""
        response = self.client.get(
            reverse("monsters:monster_update", kwargs={"pk": self.monster.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_monster_delete_url(self):
        """Test monster delete URL"""
        response = self.client.get(
            reverse("monsters:monster_delete", kwargs={"pk": self.monster.pk})
        )
        self.assertEqual(response.status_code, 200)


class MonsterIntegrationTest(TestCase):
    """Integration tests for Monster functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user)

    def test_complete_monster_lifecycle(self):
        """Test complete CRUD lifecycle for a monster"""
        # Create
        form_data = {
            "name": "Test Dragon",
            "ac": 18,
            "initiative": "+3",
            "hp": "150 (15d10 + 60)",
            "speed": "30 ft, fly 60 ft",
            "strength": "20",
            "strength_mod": "+5",
            "strength_save": "+5",
            "dexterity": "15",
            "dexterity_mod": "+2",
            "dexterity_save": "+2",
            "constitution": "18",
            "constitution_mod": "+4",
            "constitution_save": "+4",
            "intelligence": "14",
            "intelligence_mod": "+2",
            "intelligence_save": "+2",
            "wisdom": "13",
            "wisdom_mod": "+1",
            "wisdom_save": "+1",
            "charisma": "16",
            "charisma_mod": "+3",
            "charisma_save": "+3",
            "skills": "Athletics +8, Perception +4",
            "resistances": "Fire",
            "immunities": "None",
            "vulnerabilities": "Cold",
            "senses": "Darkvision 60 ft",
            "languages": "Common, Draconic",
            "gear": "Claws, Bite",
            "challenge_rating": "CR 8",
            "traits": "Fire Resistance",
            "actions": "Multiattack. The dragon makes two attacks.",
            "bonus_actions": "None",
            "reactions": "None",
            "legendary_actions": "None",
        }

        response = self.client.post(reverse("monsters:monster_create"), form_data)
        self.assertEqual(response.status_code, 302)

        # Read
        monster = Monster.objects.get(name="Test Dragon")
        self.assertEqual(monster.ac, 18)
        self.assertEqual(monster.challenge_rating, "CR 8")

        # Update
        update_data = form_data.copy()
        update_data["ac"] = 20
        update_data["challenge_rating"] = "CR 10"

        response = self.client.post(
            reverse("monsters:monster_update", kwargs={"pk": monster.pk}), update_data
        )
        self.assertEqual(response.status_code, 302)

        updated_monster = Monster.objects.get(pk=monster.pk)
        self.assertEqual(updated_monster.ac, 20)
        self.assertEqual(updated_monster.challenge_rating, "CR 10")

        # Delete
        response = self.client.post(
            reverse("monsters:monster_delete", kwargs={"pk": monster.pk})
        )
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(Monster.DoesNotExist):
            Monster.objects.get(pk=monster.pk)

    def test_multiple_monsters_search(self):
        """Test creating multiple monsters and searching"""
        # Create monsters with different characteristics
        MonsterFactory(
            name="Ancient Red Dragon",
            challenge_rating="CR 20",
            traits="Fire Breath, Legendary Resistance",
            actions="Multiattack, Fire Breath, Claw",
        )
        MonsterFactory(
            name="Goblin",
            challenge_rating="CR 1/4",
            traits="Nimble Escape",
            actions="Scimitar, Shortbow",
        )
        MonsterFactory(
            name="Orc",
            challenge_rating="CR 1/2",
            traits="Aggressive",
            actions="Greataxe, Javelin",
        )

        # Test various search queries
        search_tests = [
            ("Dragon", ["Ancient Red Dragon"]),
            ("CR 20", ["Ancient Red Dragon"]),
            ("Fire Breath", ["Ancient Red Dragon"]),
            ("Goblin", ["Goblin"]),
            ("Multiattack", ["Ancient Red Dragon"]),
            ("Orc", ["Orc"]),
        ]

        for search_term, expected_monsters in search_tests:
            response = self.client.get(
                reverse("monsters:monster_list"), {"search": search_term}
            )
            self.assertEqual(response.status_code, 200)

            for monster in expected_monsters:
                self.assertContains(response, monster)

    def test_monster_ability_score_validation(self):
        """Test monster ability score field validation"""
        form_data = {
            "name": "Test Monster",
            "ac": 15,
            "initiative": "+2",
            "hp": "50 (5d10 + 20)",
            "speed": "30 ft",
            "strength": "16",
            "strength_mod": "+3",
            "strength_save": "+3",
            "dexterity": "14",
            "dexterity_mod": "+2",
            "dexterity_save": "+2",
            "constitution": "18",
            "constitution_mod": "+4",
            "constitution_save": "+4",
            "intelligence": "12",
            "intelligence_mod": "+1",
            "intelligence_save": "+1",
            "wisdom": "13",
            "wisdom_mod": "+1",
            "wisdom_save": "+1",
            "charisma": "10",
            "charisma_mod": "+0",
            "charisma_save": "+0",
            "challenge_rating": "CR 3",
        }

        response = self.client.post(reverse("monsters:monster_create"), form_data)
        self.assertEqual(response.status_code, 302)

        monster = Monster.objects.get(name="Test Monster")

        # Verify ability scores were saved correctly
        self.assertEqual(monster.strength, "16")
        self.assertEqual(monster.strength_mod, "+3")
        self.assertEqual(monster.strength_save, "+3")
        self.assertEqual(monster.dexterity, "14")
        self.assertEqual(monster.dexterity_mod, "+2")
        self.assertEqual(monster.dexterity_save, "+2")
        self.assertEqual(monster.constitution, "18")
        self.assertEqual(monster.constitution_mod, "+4")
        self.assertEqual(monster.constitution_save, "+4")

    def test_monster_optional_fields_functionality(self):
        """Test that optional fields work correctly when provided"""
        form_data = {
            "name": "Complex Monster",
            "ac": 17,
            "initiative": "+4",
            "hp": "100 (10d10 + 40)",
            "speed": "40 ft, climb 30 ft",
            "strength": "18",
            "strength_mod": "+4",
            "strength_save": "+4",
            "dexterity": "16",
            "dexterity_mod": "+3",
            "dexterity_save": "+3",
            "constitution": "16",
            "constitution_mod": "+3",
            "constitution_save": "+3",
            "intelligence": "15",
            "intelligence_mod": "+2",
            "intelligence_save": "+2",
            "wisdom": "14",
            "wisdom_mod": "+2",
            "wisdom_save": "+2",
            "charisma": "12",
            "charisma_mod": "+1",
            "charisma_save": "+1",
            "skills": "Athletics +7, Stealth +6, Perception +5",
            "resistances": "Fire, Cold, Lightning",
            "immunities": "Poison, Charmed",
            "vulnerabilities": "Psychic",
            "senses": "Darkvision 60 ft, Tremorsense 30 ft",
            "languages": "Common, Orcish, Telepathy 30 ft",
            "gear": "Greatsword +1, Chain Mail, Shield",
            "challenge_rating": "CR 5",
            "traits": "Magic Resistance, Pack Tactics",
            "actions": "Multiattack. The monster makes two greatsword attacks.",
            "bonus_actions": "Second Wind",
            "reactions": "Parry",
            "legendary_actions": "The monster can take 2 legendary actions.",
        }

        response = self.client.post(reverse("monsters:monster_create"), form_data)
        self.assertEqual(response.status_code, 302)

        monster = Monster.objects.get(name="Complex Monster")

        # Verify optional fields were saved correctly
        self.assertEqual(monster.skills, "Athletics +7, Stealth +6, Perception +5")
        self.assertEqual(monster.resistances, "Fire, Cold, Lightning")
        self.assertEqual(monster.immunities, "Poison, Charmed")
        self.assertEqual(monster.vulnerabilities, "Psychic")
        self.assertEqual(monster.senses, "Darkvision 60 ft, Tremorsense 30 ft")
        self.assertEqual(monster.languages, "Common, Orcish, Telepathy 30 ft")
        self.assertEqual(monster.gear, "Greatsword +1, Chain Mail, Shield")
        self.assertEqual(monster.traits, "Magic Resistance, Pack Tactics")
        self.assertEqual(
            monster.actions, "Multiattack. The monster makes two greatsword attacks."
        )
        self.assertEqual(monster.bonus_actions, "Second Wind")
        self.assertEqual(monster.reactions, "Parry")
        self.assertEqual(
            monster.legendary_actions, "The monster can take 2 legendary actions."
        )
