from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from .models import PlanningSession
from campaigns.models import Campaign
from dnd_tracker.factories import UserWithProfileFactory
import factory


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campaign
    
    name = factory.Sequence(lambda n: f'Campaign {n}')
    description = factory.Faker('text', max_nb_chars=200)
    dm = factory.Faker('name')


class PlanningSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PlanningSession
    
    campaign = factory.SubFactory(CampaignFactory)
    session_date = factory.Sequence(lambda n: date.today() + timedelta(days=n))
    title = factory.Sequence(lambda n: f'Planning Session {n}')
    notes = factory.Faker('text', max_nb_chars=500)


class PlanningSessionModelTest(TestCase):
    def setUp(self):
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()
        self.planning_session = PlanningSessionFactory(campaign=self.campaign)

    def test_planning_session_creation(self):
        """Test that a planning session can be created with all required fields"""
        planning_session = PlanningSession.objects.create(
            campaign=self.campaign,
            session_date=date.today(),
            title="Test Planning Session",
            notes="A test planning session with lots of preparation notes."
        )
        self.assertEqual(planning_session.campaign, self.campaign)
        self.assertEqual(planning_session.session_date, date.today())
        self.assertEqual(planning_session.title, "Test Planning Session")
        self.assertEqual(planning_session.notes, "A test planning session with lots of preparation notes.")
        self.assertIsNotNone(planning_session.created_at)
        self.assertIsNotNone(planning_session.updated_at)

    def test_planning_session_string_representation(self):
        """Test the string representation of a planning session"""
        expected = f"{self.campaign.name} - {self.planning_session.session_date.strftime('%B %d, %Y')} - {self.planning_session.title}"
        self.assertEqual(str(self.planning_session), expected)

    def test_planning_session_ordering(self):
        """Test that planning sessions are ordered by session date (newest first) then by creation time"""
        # Clear existing planning sessions from setUp
        PlanningSession.objects.all().delete()
        
        old_planning = PlanningSessionFactory(campaign=self.campaign, session_date=date.today() - timedelta(days=7))
        new_planning = PlanningSessionFactory(campaign=self.campaign, session_date=date.today())
        
        planning_sessions = list(PlanningSession.objects.all())
        # Check that planning sessions are ordered by session date (newest first)
        self.assertEqual(planning_sessions[0], new_planning)  # Most recent date first
        self.assertEqual(planning_sessions[1], old_planning)  # Older date second

    def test_planning_session_get_absolute_url(self):
        """Test that get_absolute_url returns the correct URL"""
        expected_url = reverse('planning:planning_detail', kwargs={'pk': self.planning_session.pk})
        self.assertEqual(self.planning_session.get_absolute_url(), expected_url)

    def test_planning_session_properties(self):
        """Test planning session date properties"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        today_planning = PlanningSessionFactory(campaign=self.campaign, session_date=today)
        upcoming_planning = PlanningSessionFactory(campaign=self.campaign, session_date=tomorrow)
        past_planning = PlanningSessionFactory(campaign=self.campaign, session_date=yesterday)
        
        self.assertTrue(today_planning.is_today)
        self.assertTrue(today_planning.is_upcoming)
        self.assertFalse(today_planning.is_past)
        
        self.assertFalse(upcoming_planning.is_today)
        self.assertTrue(upcoming_planning.is_upcoming)
        self.assertFalse(upcoming_planning.is_past)
        
        self.assertFalse(past_planning.is_today)
        self.assertFalse(past_planning.is_upcoming)
        self.assertTrue(past_planning.is_past)

    def test_planning_session_unique_constraint(self):
        """Test that only one planning session per campaign per date is allowed"""
        from django.db import IntegrityError
        # Create first planning session
        PlanningSession.objects.create(
            campaign=self.campaign,
            session_date=date.today(),
            title="First Planning",
            notes="First planning session"
        )
        
        # Try to create another planning session for the same campaign and date
        with self.assertRaises(IntegrityError):
            PlanningSession.objects.create(
                campaign=self.campaign,
                session_date=date.today(),
                title="Second Planning",
                notes="Second planning session"
            )


class PlanningSessionViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()
        self.planning_session = PlanningSessionFactory(campaign=self.campaign)

    def test_planning_list_view_requires_login(self):
        """Test that planning list view requires authentication"""
        response = self.client.get(reverse('planning:planning_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_planning_list_view_with_authenticated_user(self):
        """Test that authenticated users can access planning list"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('planning:planning_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planning/planning_list.html')
        self.assertContains(response, self.planning_session.title)

    def test_planning_list_view_with_filters(self):
        """Test planning list view with various filters"""
        self.client.force_login(self.user)
        
        # Test campaign filter
        response = self.client.get(f"{reverse('planning:planning_list')}?campaign={self.campaign.pk}")
        self.assertEqual(response.status_code, 200)
        # Check that the planning session is in the context
        self.assertIn(self.planning_session, response.context['planning_sessions'])
        
        # Test search filter
        response = self.client.get(f"{reverse('planning:planning_list')}?search={self.planning_session.title}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.planning_session, response.context['planning_sessions'])

    def test_planning_detail_view_requires_login(self):
        """Test that planning detail view requires authentication"""
        response = self.client.get(reverse('planning:planning_detail', kwargs={'pk': self.planning_session.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_planning_detail_view_with_authenticated_user(self):
        """Test that authenticated users can access planning detail"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('planning:planning_detail', kwargs={'pk': self.planning_session.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planning/planning_detail.html')
        self.assertContains(response, self.planning_session.title)
        # Check that the planning session is in the context
        self.assertEqual(response.context['planning_session'], self.planning_session)

    def test_planning_create_view_requires_login(self):
        """Test that planning create view requires authentication"""
        response = self.client.get(reverse('planning:planning_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_planning_create_view_with_authenticated_user(self):
        """Test that authenticated users can access planning create form"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('planning:planning_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planning/planning_form.html')

    def test_planning_create_post_success(self):
        """Test that planning creation works with valid data"""
        self.client.force_login(self.user)
        planning_data = {
            'campaign': self.campaign.pk,
            'session_date': date.today() + timedelta(days=1),  # Use tomorrow to avoid conflict
            'title': 'A new test planning session',
            'notes': 'A new test planning session with lots of preparation notes and details.'
        }
        response = self.client.post(reverse('planning:planning_create'), planning_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('planning:planning_list'))
        
        # Check that planning session was created
        new_planning = PlanningSession.objects.get(title='A new test planning session')
        self.assertEqual(new_planning.campaign, self.campaign)
        self.assertEqual(new_planning.session_date, date.today() + timedelta(days=1))

    def test_planning_edit_view_requires_login(self):
        """Test that planning edit view requires authentication"""
        response = self.client.get(reverse('planning:planning_edit', kwargs={'pk': self.planning_session.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_planning_edit_view_with_authenticated_user(self):
        """Test that authenticated users can access planning edit form"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('planning:planning_edit', kwargs={'pk': self.planning_session.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planning/planning_form.html')

    def test_planning_edit_post_success(self):
        """Test that planning editing works with valid data"""
        self.client.force_login(self.user)
        updated_data = {
            'campaign': self.campaign.pk,
            'session_date': date.today() - timedelta(days=1),
            'title': 'Updated planning session title',
            'notes': 'Updated planning session with new information and corrected details.'
        }
        response = self.client.post(reverse('planning:planning_edit', kwargs={'pk': self.planning_session.pk}), updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('planning:planning_detail', kwargs={'pk': self.planning_session.pk}))
        
        # Check that planning session was updated
        self.planning_session.refresh_from_db()
        self.assertEqual(self.planning_session.session_date, date.today() - timedelta(days=1))
        self.assertEqual(self.planning_session.title, 'Updated planning session title')
        self.assertEqual(self.planning_session.notes, 'Updated planning session with new information and corrected details.')

    def test_planning_delete_view_requires_login(self):
        """Test that planning delete view requires authentication"""
        response = self.client.get(reverse('planning:planning_delete', kwargs={'pk': self.planning_session.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_planning_delete_view_with_authenticated_user(self):
        """Test that authenticated users can access planning delete confirmation"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('planning:planning_delete', kwargs={'pk': self.planning_session.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planning/planning_confirm_delete.html')

    def test_planning_delete_post_success(self):
        """Test that planning deletion works"""
        self.client.force_login(self.user)
        planning_id = self.planning_session.pk
        response = self.client.post(reverse('planning:planning_delete', kwargs={'pk': planning_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('planning:planning_list'))
        
        # Check that planning session was deleted
        with self.assertRaises(PlanningSession.DoesNotExist):
            PlanningSession.objects.get(pk=planning_id)

    def test_campaign_planning_view(self):
        """Test the campaign-specific planning view"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('planning:campaign_planning', kwargs={'campaign_pk': self.campaign.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'planning/campaign_planning.html')
        self.assertContains(response, self.planning_session.title)
        self.assertEqual(response.context['campaign'], self.campaign)
        # Check that the planning session is in the context
        self.assertIn(self.planning_session, response.context['planning_sessions'])


class PlanningSessionFormsTest(TestCase):
    def setUp(self):
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()

    def test_planning_form_valid_data(self):
        """Test that planning form works with valid data"""
        from .forms import PlanningSessionForm
        form_data = {
            'campaign': self.campaign.pk,
            'session_date': date.today(),
            'title': 'Test planning session',
            'notes': 'Test planning session notes'
        }
        form = PlanningSessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_planning_form_missing_required_fields(self):
        """Test that planning form validation works for required fields"""
        from .forms import PlanningSessionForm
        form_data = {
            'notes': 'Test notes'
        }
        form = PlanningSessionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('campaign', form.errors)
        self.assertIn('session_date', form.errors)
        self.assertIn('title', form.errors)

    def test_planning_form_empty_required_fields(self):
        """Test that planning form validation works for empty required fields"""
        from .forms import PlanningSessionForm
        form_data = {
            'campaign': '',
            'session_date': '',
            'title': '',
            'notes': ''
        }
        form = PlanningSessionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('campaign', form.errors)
        self.assertIn('session_date', form.errors)
        self.assertIn('title', form.errors)
        self.assertIn('notes', form.errors)


class PlanningSessionURLsTest(TestCase):
    def test_planning_list_url(self):
        """Test that planning list URL resolves correctly"""
        url = reverse('planning:planning_list')
        self.assertEqual(url, '/planning/')

    def test_planning_create_url(self):
        """Test that planning create URL resolves correctly"""
        url = reverse('planning:planning_create')
        self.assertEqual(url, '/planning/create/')

    def test_planning_detail_url(self):
        """Test that planning detail URL resolves correctly"""
        url = reverse('planning:planning_detail', kwargs={'pk': 1})
        self.assertEqual(url, '/planning/1/')

    def test_planning_edit_url(self):
        """Test that planning edit URL resolves correctly"""
        url = reverse('planning:planning_edit', kwargs={'pk': 1})
        self.assertEqual(url, '/planning/1/edit/')

    def test_planning_delete_url(self):
        """Test that planning delete URL resolves correctly"""
        url = reverse('planning:planning_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/planning/1/delete/')

    def test_campaign_planning_url(self):
        """Test that campaign planning URL resolves correctly"""
        url = reverse('planning:campaign_planning', kwargs={'campaign_pk': 1})
        self.assertEqual(url, '/planning/campaign/1/')


class PlanningSessionIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserWithProfileFactory()
        self.client.force_login(self.user)
        self.campaign = CampaignFactory()

    def test_planning_workflow(self):
        """Test the complete planning workflow: create, view, edit, delete"""
        # Create planning session
        planning_data = {
            'campaign': self.campaign.pk,
            'session_date': date.today(),
            'title': 'Integration test planning session',
            'notes': 'Integration test planning session with lots of preparation notes and details.'
        }
        response = self.client.post(reverse('planning:planning_create'), planning_data)
        self.assertEqual(response.status_code, 302)
        
        # Get the created planning session
        planning_session = PlanningSession.objects.get(title='Integration test planning session')
        
        # View planning session
        response = self.client.get(reverse('planning:planning_detail', kwargs={'pk': planning_session.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration test planning session')
        
        # Edit planning session
        updated_data = {
            'campaign': self.campaign.pk,
            'session_date': date.today() - timedelta(days=1),
            'title': 'Updated integration test planning session',
            'notes': 'Updated integration test planning session with corrected information.'
        }
        response = self.client.post(reverse('planning:planning_edit', kwargs={'pk': planning_session.pk}), updated_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify update
        planning_session.refresh_from_db()
        self.assertEqual(planning_session.session_date, date.today() - timedelta(days=1))
        self.assertEqual(planning_session.title, 'Updated integration test planning session')
        self.assertEqual(planning_session.notes, 'Updated integration test planning session with corrected information.')
        
        # Delete planning session
        response = self.client.post(reverse('planning:planning_delete', kwargs={'pk': planning_session.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Verify deletion
        with self.assertRaises(PlanningSession.DoesNotExist):
            PlanningSession.objects.get(pk=planning_session.pk)

    def test_planning_campaign_relationship(self):
        """Test that planning sessions are properly linked to campaigns"""
        planning_session = PlanningSessionFactory(campaign=self.campaign)
        
        # Test forward relationship
        self.assertEqual(planning_session.campaign, self.campaign)
        
        # Test reverse relationship
        self.assertIn(planning_session, self.campaign.planning_sessions.all())
        
        # Test campaign deletion cascades to planning sessions
        campaign_id = self.campaign.pk
        self.campaign.delete()
        with self.assertRaises(PlanningSession.DoesNotExist):
            PlanningSession.objects.get(pk=planning_session.pk)