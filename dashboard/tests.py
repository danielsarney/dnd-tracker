from django.test import TestCase, Client
from django.urls import reverse
from campaigns.models import Campaign
from characters.models import Character
from game_sessions.models import GameSession
from dnd_tracker.factories import UserWithProfileFactory
from datetime import date, timedelta
from django.utils import timezone


class DashboardViewTest(TestCase):
    def setUp(self):
        """Set up test data for dashboard tests"""
        self.client = Client()
        
        # Create test users
        self.user1 = UserWithProfileFactory()
        self.user2 = UserWithProfileFactory()
        
        # Create test campaigns
        self.campaign1 = Campaign.objects.create(
            name="Test Campaign 1",
            description="A test campaign for user 1",
            dm=self.user1.username,
            created_at=timezone.now() - timedelta(days=5)
        )
        
        self.campaign2 = Campaign.objects.create(
            name="Test Campaign 2",
            description="A test campaign for user 2",
            dm=self.user2.username,
            created_at=timezone.now() - timedelta(days=3)
        )
        
        # Create test characters
        self.character1 = Character.objects.create(
            campaign=self.campaign1,
            type='PLAYER',
            name="Test Character 1",
            race="Human",
            character_class="Fighter",
            background="A brave warrior"
        )
        
        self.character2 = Character.objects.create(
            campaign=self.campaign1,
            type='NPC',
            name="Test NPC 1",
            race="Elf",
            character_class="Wizard",
            background="A mysterious mage"
        )
        
        self.character3 = Character.objects.create(
            campaign=self.campaign2,
            type='PLAYER',
            name="Test Character 2",
            race="Dwarf",
            character_class="Cleric",
            background="A holy healer"
        )
        
        # Create test game sessions
        self.session1 = GameSession.objects.create(
            campaign=self.campaign1,
            date=date.today(),
            summary="Today's session was amazing!"
        )
        
        self.session2 = GameSession.objects.create(
            campaign=self.campaign1,
            date=date.today() + timedelta(days=1),
            summary="Tomorrow's session will be epic!"
        )
        
        self.session3 = GameSession.objects.create(
            campaign=self.campaign1,
            date=date.today() - timedelta(days=7),
            summary="Last week's session was fun!"
        )
        
        self.session4 = GameSession.objects.create(
            campaign=self.campaign2,
            date=date.today() - timedelta(days=2),
            summary="Another session in campaign 2"
        )

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_accessible_when_logged_in(self):
        """Test that dashboard is accessible when user is logged in"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard_context_data(self):
        """Test that dashboard provides correct context data"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that response has context
        self.assertIsNotNone(response.context)
        
        # Check user-specific data
        self.assertEqual(response.context['user_campaign_count'], 1)
        self.assertEqual(response.context['user_character_count'], 2)
        self.assertEqual(response.context['user_session_count'], 3)
        
        # Check character distribution
        self.assertEqual(response.context['player_characters'], 1)
        self.assertEqual(response.context['npc_characters'], 1)
        
        # Check recent activity
        self.assertEqual(response.context['recent_activity'], 3)

    def test_dashboard_shows_user_campaigns(self):
        """Test that dashboard shows only user's campaigns"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that user1's campaigns are shown
        self.assertIn(self.campaign1, response.context['user_campaigns'])
        
        # Check that user2's campaigns are not shown
        self.assertNotIn(self.campaign2, response.context['user_campaigns'])

    def test_dashboard_shows_user_characters(self):
        """Test that dashboard shows only user's characters"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that user1's characters are shown
        self.assertIn(self.character1, response.context['recent_characters'])
        self.assertIn(self.character2, response.context['recent_characters'])
        
        # Check that user2's characters are not shown
        self.assertNotIn(self.character3, response.context['recent_characters'])

    def test_dashboard_shows_user_sessions(self):
        """Test that dashboard shows only user's sessions"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that user1's sessions are shown
        self.assertIn(self.session1, response.context['recent_sessions'])
        self.assertIn(self.session2, response.context['recent_sessions'])
        self.assertIn(self.session3, response.context['recent_sessions'])
        
        # Check that user2's sessions are not shown
        self.assertNotIn(self.session4, response.context['recent_sessions'])

    def test_dashboard_shows_today_sessions(self):
        """Test that dashboard shows today's sessions"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that today's session is shown
        self.assertIn(self.session1, response.context['today_sessions'])
        
        # Check that tomorrow's session is not in today's sessions
        self.assertNotIn(self.session2, response.context['today_sessions'])

    def test_dashboard_shows_upcoming_sessions(self):
        """Test that dashboard shows upcoming sessions"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that upcoming sessions are shown
        self.assertIn(self.session2, response.context['upcoming_sessions'])
        
        # Check that past sessions are not in upcoming sessions
        self.assertNotIn(self.session3, response.context['upcoming_sessions'])

    def test_dashboard_empty_state_no_campaigns(self):
        """Test dashboard shows empty state when user has no campaigns"""
        # Create a new user with no campaigns
        new_user = UserWithProfileFactory()
        self.client.login(username=new_user.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that empty state is shown
        self.assertEqual(response.context['user_campaign_count'], 0)
        self.assertEqual(response.context['user_character_count'], 0)
        self.assertEqual(response.context['user_session_count'], 0)

    def test_dashboard_character_type_distribution(self):
        """Test that character type distribution is calculated correctly"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check character distribution
        self.assertEqual(response.context['player_characters'], 1)
        self.assertEqual(response.context['npc_characters'], 1)

    def test_dashboard_recent_activity_calculation(self):
        """Test that recent activity (30 days) is calculated correctly"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Should include sessions from last 30 days
        self.assertEqual(response.context['recent_activity'], 3)

    def test_dashboard_campaign_dm_filtering(self):
        """Test that campaigns are filtered by DM username"""
        # Create a campaign with different DM name case
        campaign3 = Campaign.objects.create(
            name="Case Test Campaign",
            description="Testing case sensitivity",
            dm=self.user1.username.upper(),  # Different case
            created_at=timezone.now()
        )
        
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Should still find the campaign due to case-insensitive filtering
        self.assertEqual(response.context['user_campaign_count'], 2)

    def test_dashboard_character_campaign_relationship(self):
        """Test that characters are found through campaign relationships"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Characters should be found through campaign relationship
        self.assertIn(self.character1, response.context['recent_characters'])
        self.assertIn(self.character2, response.context['recent_characters'])

    def test_dashboard_session_campaign_relationship(self):
        """Test that sessions are found through campaign relationships"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Sessions should be found through campaign relationship
        self.assertIn(self.session1, response.context['recent_sessions'])
        self.assertIn(self.session2, response.context['recent_sessions'])
        self.assertIn(self.session3, response.context['recent_sessions'])

    def test_dashboard_template_rendering(self):
        """Test that dashboard template renders correctly with all sections"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that all expected sections are rendered
        self.assertContains(response, 'Welcome back')
        self.assertContains(response, 'Recent Campaigns')
        self.assertContains(response, 'Recent Characters')
        self.assertContains(response, 'Character Overview')
        self.assertContains(response, 'Quick Navigation')

    def test_dashboard_quick_actions_links(self):
        """Test that quick action buttons link to correct URLs"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that quick action buttons are present
        self.assertContains(response, 'New Campaign')
        self.assertContains(response, 'New Character')
        self.assertContains(response, 'New Session')

    def test_dashboard_view_all_links(self):
        """Test that 'View All' links are present and correct"""
        self.client.login(username=self.user1.username, password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that view all links are present
        self.assertContains(response, 'View All')
        
        # Check that links point to correct URLs
        self.assertContains(response, 'campaigns/')
        self.assertContains(response, 'characters/')
        self.assertContains(response, 'sessions/')

    def test_dashboard_user_specific_data_isolation(self):
        """Test that users only see their own data"""
        # Login as user1
        self.client.login(username=self.user1.username, password='testpass123')
        response1 = self.client.get(reverse('dashboard:dashboard'))
        
        # Login as user2
        self.client.login(username=self.user2.username, password='testpass123')
        response2 = self.client.get(reverse('dashboard:dashboard'))
        
        # Check that user1 and user2 see different data
        # Both users have 1 campaign each, but they're different campaigns
        self.assertEqual(response1.context['user_campaign_count'], 1)
        self.assertEqual(response2.context['user_campaign_count'], 1)
        
        # Check that they see different campaigns
        self.assertNotEqual(
            response1.context['user_campaigns'][0].name,
            response2.context['user_campaigns'][0].name
        )
        
        # Check character counts
        self.assertEqual(response1.context['user_character_count'], 2)
        self.assertEqual(response2.context['user_character_count'], 1)
        
        # Check session counts
        self.assertEqual(response1.context['user_session_count'], 3)
        self.assertEqual(response2.context['user_session_count'], 1)


class DashboardURLTest(TestCase):
    def test_dashboard_url_pattern(self):
        """Test that dashboard URL pattern is correct"""
        url = reverse('dashboard:dashboard')
        self.assertEqual(url, '/dashboard/')

    def test_dashboard_url_resolves_to_view(self):
        """Test that dashboard URL resolves to the correct view"""
        from django.urls import resolve
        from dashboard.views import dashboard
        url = reverse('dashboard:dashboard')
        resolver = resolve(url)
        self.assertEqual(resolver.func, dashboard)


class DashboardIntegrationTest(TestCase):
    def setUp(self):
        """Set up test data for integration tests"""
        self.client = Client()
        self.user = UserWithProfileFactory()
        
        # Create a campaign
        self.campaign = Campaign.objects.create(
            name="Integration Test Campaign",
            description="Testing dashboard integration",
            dm=self.user.username
        )
        
        # Create a character
        self.character = Character.objects.create(
            campaign=self.campaign,
            type='PLAYER',
            name="Integration Test Character",
            race="Human",
            character_class="Rogue"
        )
        
        # Create a session
        self.session = GameSession.objects.create(
            campaign=self.campaign,
            date=date.today(),
            summary="Integration test session"
        )

    def test_dashboard_full_user_journey(self):
        """Test complete user journey through dashboard"""
        # Login
        self.client.login(username=self.user.username, password='testpass123')
        
        # Access dashboard
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check that all user data is displayed
        self.assertContains(response, self.campaign.name)
        self.assertContains(response, self.character.name)
        self.assertContains(response, self.session.summary)
        
        # Check that quick actions work
        self.assertContains(response, 'New Campaign')
        self.assertContains(response, 'New Character')
        self.assertContains(response, 'New Session')

    def test_dashboard_navigation_flow(self):
        """Test navigation flow from dashboard to other sections"""
        self.client.login(username=self.user.username, password='testpass123')
        
        # Start at dashboard
        dashboard_response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        
        # Navigate to campaigns
        campaigns_response = self.client.get(reverse('campaigns:campaign_list'))
        self.assertEqual(campaigns_response.status_code, 200)
        
        # Navigate to characters
        characters_response = self.client.get(reverse('characters:character_list'))
        self.assertEqual(characters_response.status_code, 200)
        
        # Navigate to sessions
        sessions_response = self.client.get(reverse('game_sessions:session_list'))
        self.assertEqual(sessions_response.status_code, 200)
        
        # Navigate back to dashboard
        dashboard_response2 = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(dashboard_response2.status_code, 200)
