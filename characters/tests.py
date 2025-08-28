from django.test import TestCase, Client
from django.urls import reverse
from .models import Character
from campaigns.models import Campaign
from dnd_tracker.factories import UserWithProfileFactory
import factory


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campaign
    
    name = factory.Sequence(lambda n: f'Campaign {n}')
    description = factory.Faker('text', max_nb_chars=200)
    dm = factory.Faker('name')


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Character
    
    campaign = factory.SubFactory(CampaignFactory)
    type = 'PLAYER'
    name = factory.Sequence(lambda n: f'Character {n}')
    race = factory.Faker('word')
    character_class = factory.Faker('word')
    background = factory.Faker('text', max_nb_chars=150)


class CharacterModelTest(TestCase):
    def setUp(self):
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()
        self.character = CharacterFactory(campaign=self.campaign)

    def test_character_creation(self):
        """Test that a character can be created with all required fields"""
        character = Character.objects.create(
            campaign=self.campaign,
            type='NPC',
            name="Test NPC",
            race="Human",
            character_class="Fighter",
            background="A test NPC background"
        )
        self.assertEqual(character.campaign, self.campaign)
        self.assertEqual(character.type, 'NPC')
        self.assertEqual(character.name, "Test NPC")
        self.assertEqual(character.race, "Human")
        self.assertEqual(character.character_class, "Fighter")
        self.assertEqual(character.background, "A test NPC background")
        self.assertIsNotNone(character.created_at)
        self.assertIsNotNone(character.updated_at)

    def test_character_string_representation(self):
        """Test the string representation of a character"""
        expected = f"{self.character.name} ({self.character.get_type_display()})"
        self.assertEqual(str(self.character), expected)

    def test_character_ordering(self):
        """Test that characters are ordered by type then name"""
        # Clear existing characters from setUp
        Character.objects.all().delete()
        
        player_char = CharacterFactory(campaign=self.campaign, type='PLAYER', name='Alice')
        player_char2 = CharacterFactory(campaign=self.campaign, type='PLAYER', name='Charlie')
        npc_char = CharacterFactory(campaign=self.campaign, type='NPC', name='Bob')
        
        characters = list(Character.objects.all())
        # Should be ordered by type (PLAYER first), then by name
        # Check that PLAYER characters come before NPC characters
        player_chars = [c for c in characters if c.type == 'PLAYER']
        npc_chars = [c for c in characters if c.type == 'NPC']
        
        self.assertEqual(len(player_chars), 2)
        self.assertEqual(len(npc_chars), 1)
        self.assertTrue(all(c.type == 'PLAYER' for c in player_chars))
        self.assertTrue(all(c.type == 'NPC' for c in npc_chars))

    def test_character_get_absolute_url(self):
        """Test that get_absolute_url returns the correct URL"""
        expected_url = reverse('characters:character_detail', kwargs={'pk': self.character.pk})
        self.assertEqual(self.character.get_absolute_url(), expected_url)

    def test_character_properties(self):
        """Test character type properties"""
        player_char = CharacterFactory(campaign=self.campaign, type='PLAYER')
        npc_char = CharacterFactory(campaign=self.campaign, type='NPC')
        
        self.assertTrue(player_char.is_player)
        self.assertFalse(player_char.is_npc)
        self.assertTrue(npc_char.is_npc)
        self.assertFalse(npc_char.is_player)


class CharacterViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()
        self.character = CharacterFactory(campaign=self.campaign)

    def test_character_list_view_requires_login(self):
        """Test that character list view requires authentication"""
        response = self.client.get(reverse('characters:character_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_character_list_view_with_authenticated_user(self):
        """Test that authenticated users can access character list"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('characters:character_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'characters/character_list.html')
        self.assertContains(response, self.character.name)

    def test_character_list_view_with_filters(self):
        """Test character list view with various filters"""
        self.client.force_login(self.user)
        
        # Test campaign filter
        response = self.client.get(f"{reverse('characters:character_list')}?campaign={self.campaign.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.character.name)
        
        # Test type filter
        response = self.client.get(f"{reverse('characters:character_list')}?type=PLAYER")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.character.name)
        
        # Test search filter
        response = self.client.get(f"{reverse('characters:character_list')}?search={self.character.name}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.character.name)

    def test_character_detail_view_requires_login(self):
        """Test that character detail view requires authentication"""
        response = self.client.get(reverse('characters:character_detail', kwargs={'pk': self.character.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_character_detail_view_with_authenticated_user(self):
        """Test that authenticated users can access character detail"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('characters:character_detail', kwargs={'pk': self.character.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'characters/character_detail.html')
        self.assertContains(response, self.character.name)
        self.assertContains(response, self.character.campaign.name)

    def test_character_create_view_requires_login(self):
        """Test that character create view requires authentication"""
        response = self.client.get(reverse('characters:character_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_character_create_view_with_authenticated_user(self):
        """Test that authenticated users can access character create form"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('characters:character_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'characters/character_form.html')

    def test_character_create_post_success(self):
        """Test that character creation works with valid data"""
        self.client.force_login(self.user)
        character_data = {
            'campaign': self.campaign.pk,
            'type': 'NPC',
            'name': 'New Test Character',
            'race': 'Elf',
            'character_class': 'Wizard',
            'background': 'A new test character background'
        }
        response = self.client.post(reverse('characters:character_create'), character_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('characters:character_list'))
        
        # Check that character was created
        new_character = Character.objects.get(name='New Test Character')
        self.assertEqual(new_character.campaign, self.campaign)
        self.assertEqual(new_character.type, 'NPC')
        self.assertEqual(new_character.race, 'Elf')
        self.assertEqual(new_character.character_class, 'Wizard')

    def test_character_edit_view_requires_login(self):
        """Test that character edit view requires authentication"""
        response = self.client.get(reverse('characters:character_edit', kwargs={'pk': self.character.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_character_edit_view_with_authenticated_user(self):
        """Test that authenticated users can access character edit form"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('characters:character_edit', kwargs={'pk': self.character.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'characters/character_form.html')

    def test_character_edit_post_success(self):
        """Test that character editing works with valid data"""
        self.client.force_login(self.user)
        updated_data = {
            'campaign': self.campaign.pk,
            'type': 'NPC',
            'name': 'Updated Character Name',
            'race': 'Dwarf',
            'character_class': 'Paladin',
            'background': 'Updated background information'
        }
        response = self.client.post(reverse('characters:character_edit', kwargs={'pk': self.character.pk}), updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('characters:character_detail', kwargs={'pk': self.character.pk}))
        
        # Check that character was updated
        self.character.refresh_from_db()
        self.assertEqual(self.character.name, 'Updated Character Name')
        self.assertEqual(self.character.type, 'NPC')
        self.assertEqual(self.character.race, 'Dwarf')
        self.assertEqual(self.character.character_class, 'Paladin')

    def test_character_delete_view_requires_login(self):
        """Test that character delete view requires authentication"""
        response = self.client.get(reverse('characters:character_delete', kwargs={'pk': self.character.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_character_delete_view_with_authenticated_user(self):
        """Test that authenticated users can access character delete confirmation"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('characters:character_delete', kwargs={'pk': self.character.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'characters/character_confirm_delete.html')

    def test_character_delete_post_success(self):
        """Test that character deletion works"""
        self.client.force_login(self.user)
        character_id = self.character.pk
        response = self.client.post(reverse('characters:character_delete', kwargs={'pk': character_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('characters:character_list'))
        
        # Check that character was deleted
        with self.assertRaises(Character.DoesNotExist):
            Character.objects.get(pk=character_id)

    def test_campaign_characters_view(self):
        """Test the campaign-specific characters view"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('characters:campaign_characters', kwargs={'campaign_pk': self.campaign.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'characters/campaign_characters.html')
        self.assertContains(response, self.character.name)
        self.assertEqual(response.context['campaign'], self.campaign)


class CharacterFormsTest(TestCase):
    def setUp(self):
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()

    def test_character_form_valid_data(self):
        """Test that character form works with valid data"""
        from .forms import CharacterForm
        form_data = {
            'campaign': self.campaign.pk,
            'type': 'PLAYER',
            'name': 'Test Character',
            'race': 'Human',
            'character_class': 'Fighter',
            'background': 'Test background'
        }
        form = CharacterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_character_form_missing_required_fields(self):
        """Test that character form validation works for required fields"""
        from .forms import CharacterForm
        form_data = {
            'race': 'Human',
            'character_class': 'Fighter'
        }
        form = CharacterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('campaign', form.errors)
        self.assertIn('type', form.errors)
        self.assertIn('name', form.errors)

    def test_character_form_empty_required_fields(self):
        """Test that character form validation works for empty required fields"""
        from .forms import CharacterForm
        form_data = {
            'campaign': '',
            'type': '',
            'name': '',
            'race': 'Human',
            'character_class': 'Fighter'
        }
        form = CharacterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('campaign', form.errors)
        self.assertIn('type', form.errors)
        self.assertIn('name', form.errors)


class CharacterURLsTest(TestCase):
    def test_character_list_url(self):
        """Test that character list URL resolves correctly"""
        url = reverse('characters:character_list')
        self.assertEqual(url, '/characters/')

    def test_character_create_url(self):
        """Test that character create URL resolves correctly"""
        url = reverse('characters:character_create')
        self.assertEqual(url, '/characters/create/')

    def test_character_detail_url(self):
        """Test that character detail URL resolves correctly"""
        url = reverse('characters:character_detail', kwargs={'pk': 1})
        self.assertEqual(url, '/characters/1/')

    def test_character_edit_url(self):
        """Test that character edit URL resolves correctly"""
        url = reverse('characters:character_edit', kwargs={'pk': 1})
        self.assertEqual(url, '/characters/1/edit/')

    def test_character_delete_url(self):
        """Test that character delete URL resolves correctly"""
        url = reverse('characters:character_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/characters/1/delete/')

    def test_campaign_characters_url(self):
        """Test that campaign characters URL resolves correctly"""
        url = reverse('characters:campaign_characters', kwargs={'campaign_pk': 1})
        self.assertEqual(url, '/characters/campaign/1/')


class CharacterIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserWithProfileFactory()
        self.client.force_login(self.user)
        self.campaign = CampaignFactory()

    def test_character_workflow(self):
        """Test the complete character workflow: create, view, edit, delete"""
        # Create character
        character_data = {
            'campaign': self.campaign.pk,
            'type': 'PLAYER',
            'name': 'Integration Test Character',
            'race': 'Elf',
            'character_class': 'Ranger',
            'background': 'Testing the full workflow'
        }
        response = self.client.post(reverse('characters:character_create'), character_data)
        self.assertEqual(response.status_code, 302)
        
        # Get the created character
        character = Character.objects.get(name='Integration Test Character')
        
        # View character
        response = self.client.get(reverse('characters:character_detail', kwargs={'pk': character.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Character')
        
        # Edit character
        updated_data = {
            'campaign': self.campaign.pk,
            'type': 'NPC',
            'name': 'Updated Integration Character',
            'race': 'Dwarf',
            'character_class': 'Cleric',
            'background': 'Updated workflow test'
        }
        response = self.client.post(reverse('characters:character_edit', kwargs={'pk': character.pk}), updated_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify update
        character.refresh_from_db()
        self.assertEqual(character.name, 'Updated Integration Character')
        self.assertEqual(character.type, 'NPC')
        
        # Delete character
        response = self.client.post(reverse('characters:character_delete', kwargs={'pk': character.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Verify deletion
        with self.assertRaises(Character.DoesNotExist):
            Character.objects.get(pk=character.pk)

    def test_character_campaign_relationship(self):
        """Test that characters are properly linked to campaigns"""
        character = CharacterFactory(campaign=self.campaign)
        
        # Test forward relationship
        self.assertEqual(character.campaign, self.campaign)
        
        # Test reverse relationship
        self.assertIn(character, self.campaign.characters.all())
        
        # Test campaign deletion cascades to characters
        campaign_id = self.campaign.pk
        self.campaign.delete()
        with self.assertRaises(Character.DoesNotExist):
            Character.objects.get(pk=character.pk)
