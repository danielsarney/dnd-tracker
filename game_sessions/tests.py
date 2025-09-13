from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from .models import GameSession
from campaigns.models import Campaign
from dnd_tracker.factories import UserWithProfileFactory
import factory


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campaign
    
    name = factory.Sequence(lambda n: f'Campaign {n}')
    description = factory.Faker('text', max_nb_chars=200)
    dm = factory.Faker('name')


class GameSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GameSession
    
    campaign = factory.SubFactory(CampaignFactory)
    date = factory.LazyFunction(lambda: date.today())
    summary = factory.Faker('text', max_nb_chars=100)


class GameSessionModelTest(TestCase):
    def setUp(self):
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()
        self.session = GameSessionFactory(campaign=self.campaign)

    def test_session_creation(self):
        """Test that a game session can be created with all required fields"""
        session = GameSession.objects.create(
            campaign=self.campaign,
            date=date.today(),
            summary="A test session summary with lots of details about what happened."
        )
        self.assertEqual(session.campaign, self.campaign)
        self.assertEqual(session.date, date.today())
        self.assertEqual(session.summary, "A test session summary with lots of details about what happened.")
        self.assertIsNotNone(session.created_at)
        self.assertIsNotNone(session.updated_at)

    def test_session_string_representation(self):
        """Test the string representation of a game session"""
        expected = f"{self.campaign.name} - {self.session.date.strftime('%B %d, %Y')}"
        self.assertEqual(str(self.session), expected)

    def test_session_ordering(self):
        """Test that sessions are ordered by date (newest first) then by creation time"""
        # Clear existing sessions from setUp
        GameSession.objects.all().delete()
        
        old_session = GameSessionFactory(campaign=self.campaign, date=date.today() - timedelta(days=7))
        new_session = GameSessionFactory(campaign=self.campaign, date=date.today())
        
        sessions = list(GameSession.objects.all())
        # Check that sessions are ordered by date (newest first)
        self.assertEqual(sessions[0], new_session)  # Most recent date first
        self.assertEqual(sessions[1], old_session)  # Older date second

    def test_session_get_absolute_url(self):
        """Test that get_absolute_url returns the correct URL"""
        expected_url = reverse('game_sessions:session_detail', kwargs={'pk': self.session.pk})
        self.assertEqual(self.session.get_absolute_url(), expected_url)

    def test_session_properties(self):
        """Test session date properties"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=8)
        
        today_session = GameSessionFactory(campaign=self.campaign, date=today)
        recent_session = GameSessionFactory(campaign=self.campaign, date=yesterday)
        old_session = GameSessionFactory(campaign=self.campaign, date=week_ago)
        
        self.assertTrue(today_session.is_today)
        self.assertTrue(today_session.is_recent)
        self.assertFalse(recent_session.is_today)
        self.assertTrue(recent_session.is_recent)
        self.assertFalse(old_session.is_today)
        self.assertFalse(old_session.is_recent)


class GameSessionViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()
        self.session = GameSessionFactory(campaign=self.campaign)

    def test_session_list_view_requires_login(self):
        """Test that session list view requires authentication"""
        response = self.client.get(reverse('game_sessions:session_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_session_list_view_with_authenticated_user(self):
        """Test that authenticated users can access session list"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('game_sessions:session_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_sessions/session_list.html')
        self.assertContains(response, self.session.campaign.name)

    def test_session_list_view_with_filters(self):
        """Test session list view with various filters"""
        self.client.force_login(self.user)
        
        # Test campaign filter
        response = self.client.get(f"{reverse('game_sessions:session_list')}?campaign={self.campaign.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session.campaign.name)
        
        # Test search filter
        response = self.client.get(f"{reverse('game_sessions:session_list')}?search={self.campaign.name}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session.campaign.name)

    def test_session_detail_view_requires_login(self):
        """Test that session detail view requires authentication"""
        response = self.client.get(reverse('game_sessions:session_detail', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_session_detail_view_with_authenticated_user(self):
        """Test that authenticated users can access session detail"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('game_sessions:session_detail', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_sessions/session_detail.html')
        self.assertContains(response, self.session.campaign.name)
        self.assertContains(response, self.session.summary)

    def test_session_create_view_requires_login(self):
        """Test that session create view requires authentication"""
        response = self.client.get(reverse('game_sessions:session_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_session_create_view_with_authenticated_user(self):
        """Test that authenticated users can access session create form"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('game_sessions:session_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_sessions/session_form.html')

    def test_session_create_post_success(self):
        """Test that session creation works with valid data"""
        self.client.force_login(self.user)
        session_data = {
            'campaign': self.campaign.pk,
            'date': date.today(),
            'summary': 'A new test session with lots of exciting events and character development.'
        }
        response = self.client.post(reverse('game_sessions:session_create'), session_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('game_sessions:session_list'))
        
        # Check that session was created
        new_session = GameSession.objects.get(summary='A new test session with lots of exciting events and character development.')
        self.assertEqual(new_session.campaign, self.campaign)
        self.assertEqual(new_session.date, date.today())

    def test_session_edit_view_requires_login(self):
        """Test that session edit view requires authentication"""
        response = self.client.get(reverse('game_sessions:session_edit', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_session_edit_view_with_authenticated_user(self):
        """Test that authenticated users can access session edit form"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('game_sessions:session_edit', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_sessions/session_form.html')

    def test_session_edit_post_success(self):
        """Test that session editing works with valid data"""
        self.client.force_login(self.user)
        updated_data = {
            'campaign': self.campaign.pk,
            'date': date.today() - timedelta(days=1),
            'summary': 'Updated session summary with new information and corrected details.'
        }
        response = self.client.post(reverse('game_sessions:session_edit', kwargs={'pk': self.session.pk}), updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('game_sessions:session_detail', kwargs={'pk': self.session.pk}))
        
        # Check that session was updated
        self.session.refresh_from_db()
        self.assertEqual(self.session.date, date.today() - timedelta(days=1))
        self.assertEqual(self.session.summary, 'Updated session summary with new information and corrected details.')

    def test_session_delete_view_requires_login(self):
        """Test that session delete view requires authentication"""
        response = self.client.get(reverse('game_sessions:session_delete', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_session_delete_view_with_authenticated_user(self):
        """Test that authenticated users can access session delete confirmation"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('game_sessions:session_delete', kwargs={'pk': self.session.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_sessions/session_confirm_delete.html')

    def test_session_delete_post_success(self):
        """Test that session deletion works"""
        self.client.force_login(self.user)
        session_id = self.session.pk
        response = self.client.post(reverse('game_sessions:session_delete', kwargs={'pk': session_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('game_sessions:session_list'))
        
        # Check that session was deleted
        with self.assertRaises(GameSession.DoesNotExist):
            GameSession.objects.get(pk=session_id)

    def test_campaign_sessions_view(self):
        """Test the campaign-specific sessions view"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('game_sessions:campaign_sessions', kwargs={'campaign_pk': self.campaign.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game_sessions/campaign_sessions.html')
        self.assertContains(response, self.session.summary)
        self.assertEqual(response.context['campaign'], self.campaign)


class GameSessionFormsTest(TestCase):
    def setUp(self):
        self.user = UserWithProfileFactory()
        self.campaign = CampaignFactory()

    def test_session_form_valid_data(self):
        """Test that session form works with valid data"""
        from .forms import GameSessionForm
        form_data = {
            'campaign': self.campaign.pk,
            'date': date.today(),
            'summary': 'Test session summary'
        }
        form = GameSessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_session_form_missing_required_fields(self):
        """Test that session form validation works for required fields"""
        from .forms import GameSessionForm
        form_data = {
            'summary': 'Test summary'
        }
        form = GameSessionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('campaign', form.errors)
        self.assertIn('date', form.errors)

    def test_session_form_empty_required_fields(self):
        """Test that session form validation works for empty required fields"""
        from .forms import GameSessionForm
        form_data = {
            'campaign': '',
            'date': '',
            'summary': ''
        }
        form = GameSessionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('campaign', form.errors)
        self.assertIn('date', form.errors)
        self.assertIn('summary', form.errors)


class GameSessionURLsTest(TestCase):
    def test_session_list_url(self):
        """Test that session list URL resolves correctly"""
        url = reverse('game_sessions:session_list')
        self.assertEqual(url, '/sessions/')

    def test_session_create_url(self):
        """Test that session create URL resolves correctly"""
        url = reverse('game_sessions:session_create')
        self.assertEqual(url, '/sessions/create/')

    def test_session_detail_url(self):
        """Test that session detail URL resolves correctly"""
        url = reverse('game_sessions:session_detail', kwargs={'pk': 1})
        self.assertEqual(url, '/sessions/1/')

    def test_session_edit_url(self):
        """Test that session edit URL resolves correctly"""
        url = reverse('game_sessions:session_edit', kwargs={'pk': 1})
        self.assertEqual(url, '/sessions/1/edit/')

    def test_session_delete_url(self):
        """Test that session delete URL resolves correctly"""
        url = reverse('game_sessions:session_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/sessions/1/delete/')

    def test_campaign_sessions_url(self):
        """Test that campaign sessions URL resolves correctly"""
        url = reverse('game_sessions:campaign_sessions', kwargs={'campaign_pk': 1})
        self.assertEqual(url, '/sessions/campaign/1/')


class GameSessionIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserWithProfileFactory()
        self.client.force_login(self.user)
        self.campaign = CampaignFactory()

    def test_session_workflow(self):
        """Test the complete session workflow: create, view, edit, delete"""
        # Create session
        session_data = {
            'campaign': self.campaign.pk,
            'date': date.today(),
            'summary': 'Integration test session with lots of exciting events and character development.'
        }
        response = self.client.post(reverse('game_sessions:session_create'), session_data)
        self.assertEqual(response.status_code, 302)
        
        # Get the created session
        session = GameSession.objects.get(summary='Integration test session with lots of exciting events and character development.')
        
        # View session
        response = self.client.get(reverse('game_sessions:session_detail', kwargs={'pk': session.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration test session with lots of exciting events and character development.')
        
        # Edit session
        updated_data = {
            'campaign': self.campaign.pk,
            'date': date.today() - timedelta(days=1),
            'summary': 'Updated integration test session with corrected information.'
        }
        response = self.client.post(reverse('game_sessions:session_edit', kwargs={'pk': session.pk}), updated_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify update
        session.refresh_from_db()
        self.assertEqual(session.date, date.today() - timedelta(days=1))
        self.assertEqual(session.summary, 'Updated integration test session with corrected information.')
        
        # Delete session
        response = self.client.post(reverse('game_sessions:session_delete', kwargs={'pk': session.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Verify deletion
        with self.assertRaises(GameSession.DoesNotExist):
            GameSession.objects.get(pk=session.pk)

    def test_session_campaign_relationship(self):
        """Test that sessions are properly linked to campaigns"""
        session = GameSessionFactory(campaign=self.campaign)
        
        # Test forward relationship
        self.assertEqual(session.campaign, self.campaign)
        
        # Test reverse relationship
        self.assertIn(session, self.campaign.sessions.all())
        
        # Test campaign deletion cascades to sessions
        campaign_id = self.campaign.pk
        self.campaign.delete()
        with self.assertRaises(GameSession.DoesNotExist):
            GameSession.objects.get(pk=session.pk)
