from django.test import TestCase, Client
from django.urls import reverse
from .models import Campaign
from dnd_tracker.factories import UserWithProfileFactory
import factory


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campaign
    
    name = factory.Sequence(lambda n: f'Campaign {n}')
    description = factory.Faker('text', max_nb_chars=200)
    dm = factory.Faker('name')


class CampaignModelTest(TestCase):
    def setUp(self):
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()

    def test_campaign_creation(self):
        """Test that a campaign can be created with all required fields"""
        campaign = Campaign.objects.create(
            name="Test Campaign",
            description="A test campaign description",
            dm="Test DM"
        )
        self.assertEqual(campaign.name, "Test Campaign")
        self.assertEqual(campaign.dm, "Test DM")
        self.assertEqual(campaign.description, "A test campaign description")
        self.assertIsNotNone(campaign.created_at)
        self.assertIsNotNone(campaign.updated_at)

    def test_campaign_string_representation(self):
        """Test the string representation of a campaign"""
        self.assertEqual(str(self.campaign), self.campaign.name)

    def test_campaign_ordering(self):
        """Test that campaigns are ordered by creation date (newest first)"""
        campaign1 = CampaignFactory()
        campaign2 = CampaignFactory()
        campaigns = Campaign.objects.all()
        self.assertEqual(campaigns[0], campaign2)
        self.assertEqual(campaigns[1], campaign1)

    def test_campaign_get_absolute_url(self):
        """Test that get_absolute_url returns the correct URL"""
        expected_url = reverse('campaigns:campaign_detail', kwargs={'pk': self.campaign.pk})
        self.assertEqual(self.campaign.get_absolute_url(), expected_url)


class CampaignViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()

    def test_campaign_list_view_requires_login(self):
        """Test that campaign list view requires authentication"""
        response = self.client.get(reverse('campaigns:campaign_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_campaign_list_view_with_authenticated_user(self):
        """Test that authenticated users can access campaign list"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('campaigns:campaign_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campaigns/campaign_list.html')
        self.assertContains(response, self.campaign.name)

    def test_campaign_detail_view_requires_login(self):
        """Test that campaign detail view requires authentication"""
        response = self.client.get(reverse('campaigns:campaign_detail', kwargs={'pk': self.campaign.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_campaign_detail_view_with_authenticated_user(self):
        """Test that authenticated users can access campaign detail"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('campaigns:campaign_detail', kwargs={'pk': self.campaign.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campaigns/campaign_detail.html')
        self.assertContains(response, self.campaign.name)
        self.assertContains(response, self.campaign.dm)

    def test_campaign_create_view_requires_login(self):
        """Test that campaign create view requires authentication"""
        response = self.client.get(reverse('campaigns:campaign_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_campaign_create_view_with_authenticated_user(self):
        """Test that authenticated users can access campaign create form"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('campaigns:campaign_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campaigns/campaign_form.html')

    def test_campaign_create_post_success(self):
        """Test that campaign creation works with valid data"""
        self.client.force_login(self.user)
        campaign_data = {
            'name': 'New Test Campaign',
            'description': 'A new test campaign',
            'dm': 'New Test DM'
        }
        response = self.client.post(reverse('campaigns:campaign_create'), campaign_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('campaigns:campaign_list'))
        
        # Check that campaign was created
        new_campaign = Campaign.objects.get(name='New Test Campaign')
        self.assertEqual(new_campaign.dm, 'New Test DM')
        self.assertEqual(new_campaign.description, 'A new test campaign')

    def test_campaign_edit_view_requires_login(self):
        """Test that campaign edit view requires authentication"""
        response = self.client.get(reverse('campaigns:campaign_edit', kwargs={'pk': self.campaign.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_campaign_edit_view_with_authenticated_user(self):
        """Test that authenticated users can access campaign edit form"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('campaigns:campaign_edit', kwargs={'pk': self.campaign.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campaigns/campaign_form.html')

    def test_campaign_edit_post_success(self):
        """Test that campaign editing works with valid data"""
        self.client.force_login(self.user)
        updated_data = {
            'name': 'Updated Campaign Name',
            'description': 'Updated description',
            'dm': 'Updated DM Name'
        }
        response = self.client.post(reverse('campaigns:campaign_edit', kwargs={'pk': self.campaign.pk}), updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('campaigns:campaign_detail', kwargs={'pk': self.campaign.pk}))
        
        # Check that campaign was updated
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.name, 'Updated Campaign Name')
        self.assertEqual(self.campaign.dm, 'Updated DM Name')
        self.assertEqual(self.campaign.description, 'Updated description')

    def test_campaign_delete_view_requires_login(self):
        """Test that campaign delete view requires authentication"""
        response = self.client.get(reverse('campaigns:campaign_delete', kwargs={'pk': self.campaign.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_campaign_delete_view_with_authenticated_user(self):
        """Test that authenticated users can access campaign delete confirmation"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('campaigns:campaign_delete', kwargs={'pk': self.campaign.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campaigns/campaign_confirm_delete.html')

    def test_campaign_delete_post_success(self):
        """Test that campaign deletion works"""
        self.client.force_login(self.user)
        campaign_id = self.campaign.pk
        response = self.client.post(reverse('campaigns:campaign_delete', kwargs={'pk': campaign_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('campaigns:campaign_list'))
        
        # Check that campaign was deleted
        with self.assertRaises(Campaign.DoesNotExist):
            Campaign.objects.get(pk=campaign_id)


class CampaignFormsTest(TestCase):
    def setUp(self):
        self.user = UserWithProfileFactory()

    def test_campaign_form_valid_data(self):
        """Test that campaign form works with valid data"""
        from .forms import CampaignForm
        form_data = {
            'name': 'Test Campaign',
            'description': 'Test description',
            'dm': 'Test DM'
        }
        form = CampaignForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_campaign_form_missing_required_fields(self):
        """Test that campaign form validation works for required fields"""
        from .forms import CampaignForm
        form_data = {
            'description': 'Test description'
        }
        form = CampaignForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('dm', form.errors)

    def test_campaign_form_empty_required_fields(self):
        """Test that campaign form validation works for empty required fields"""
        from .forms import CampaignForm
        form_data = {
            'name': '',
            'dm': '',
            'description': 'Test description'
        }
        form = CampaignForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('dm', form.errors)


class CampaignURLsTest(TestCase):
    def test_campaign_list_url(self):
        """Test that campaign list URL resolves correctly"""
        url = reverse('campaigns:campaign_list')
        self.assertEqual(url, '/campaigns/')

    def test_campaign_create_url(self):
        """Test that campaign create URL resolves correctly"""
        url = reverse('campaigns:campaign_create')
        self.assertEqual(url, '/campaigns/create/')

    def test_campaign_detail_url(self):
        """Test that campaign detail URL resolves correctly"""
        url = reverse('campaigns:campaign_detail', kwargs={'pk': 1})
        self.assertEqual(url, '/campaigns/1/')

    def test_campaign_edit_url(self):
        """Test that campaign edit URL resolves correctly"""
        url = reverse('campaigns:campaign_edit', kwargs={'pk': 1})
        self.assertEqual(url, '/campaigns/1/edit/')

    def test_campaign_delete_url(self):
        """Test that campaign delete URL resolves correctly"""
        url = reverse('campaigns:campaign_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/campaigns/1/delete/')


class CampaignIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserWithProfileFactory()
        self.client.force_login(self.user)

    def test_campaign_workflow(self):
        """Test the complete campaign workflow: create, view, edit, delete"""
        # Create campaign
        campaign_data = {
            'name': 'Integration Test Campaign',
            'description': 'Testing the full workflow',
            'dm': 'Integration Test DM'
        }
        response = self.client.post(reverse('campaigns:campaign_create'), campaign_data)
        self.assertEqual(response.status_code, 302)
        
        # Get the created campaign
        campaign = Campaign.objects.get(name='Integration Test Campaign')
        
        # View campaign
        response = self.client.get(reverse('campaigns:campaign_detail', kwargs={'pk': campaign.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Campaign')
        
        # Edit campaign
        updated_data = {
            'name': 'Updated Integration Campaign',
            'description': 'Updated workflow test',
            'dm': 'Updated Integration DM'
        }
        response = self.client.post(reverse('campaigns:campaign_edit', kwargs={'pk': campaign.pk}), updated_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify update
        campaign.refresh_from_db()
        self.assertEqual(campaign.name, 'Updated Integration Campaign')
        
        # Delete campaign
        response = self.client.post(reverse('campaigns:campaign_delete', kwargs={'pk': campaign.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Verify deletion
        with self.assertRaises(Campaign.DoesNotExist):
            Campaign.objects.get(pk=campaign.pk)
