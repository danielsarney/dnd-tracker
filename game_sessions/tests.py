from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django import forms
from datetime import date, timedelta
from dnd_tracker.factories import UserFactory, CampaignFactory, SessionFactory
from game_sessions.models import Session
from game_sessions.forms import SessionForm

User = get_user_model()


class SessionModelTest(TestCase):
    """Test cases for Session model"""

    def setUp(self):
        """Set up test data"""
        self.campaign = CampaignFactory()
        self.session = SessionFactory(campaign=self.campaign)

    def test_session_creation(self):
        """Test that a session can be created with all fields"""
        self.assertIsInstance(self.session, Session)
        self.assertEqual(self.session.campaign, self.campaign)
        self.assertTrue(self.session.planning_notes)
        self.assertTrue(self.session.session_notes)
        self.assertTrue(self.session.session_date)

    def test_session_str_representation(self):
        """Test the string representation of Session"""
        expected = f"{self.campaign.title} - {self.session.session_date}"
        self.assertEqual(str(self.session), expected)

    def test_session_campaign_required(self):
        """Test that campaign is required"""
        with self.assertRaises(IntegrityError):
            Session.objects.create(
                campaign=None,
                planning_notes="Test planning notes",
                session_notes="Test session notes",
                session_date=date.today(),
            )

    def test_session_optional_fields(self):
        """Test that optional fields can be empty"""
        session = Session.objects.create(
            campaign=self.campaign,
            planning_notes="",
            session_notes="",
            session_date=None,
        )
        self.assertEqual(session.campaign, self.campaign)
        self.assertEqual(session.planning_notes, "")
        self.assertEqual(session.session_notes, "")
        self.assertIsNone(session.session_date)

    def test_session_ordering(self):
        """Test that sessions are ordered by session_date descending, then campaign title"""
        # Create sessions with different dates
        old_date = date.today() - timedelta(days=30)
        recent_date = date.today()

        session_old = SessionFactory(campaign=self.campaign, session_date=old_date)
        session_recent = SessionFactory(
            campaign=self.campaign, session_date=recent_date
        )

        sessions = Session.objects.all()
        # Most recent first
        self.assertEqual(sessions[0], session_recent)
        self.assertEqual(sessions[1], session_old)

    def test_session_campaign_relationship(self):
        """Test the relationship between Session and Campaign"""
        self.assertEqual(self.session.campaign, self.campaign)
        self.assertIn(self.session, self.campaign.sessions.all())

    def test_session_date_field_type(self):
        """Test that session_date is a DateField"""
        self.assertIsInstance(self.session.session_date, date)

    def test_session_text_fields(self):
        """Test that text fields can handle long content"""
        long_text = "A" * 1000
        session = Session.objects.create(
            campaign=self.campaign,
            planning_notes=long_text,
            session_notes=long_text,
            session_date=date.today(),
        )
        self.assertEqual(len(session.planning_notes), 1000)
        self.assertEqual(len(session.session_notes), 1000)


class SessionFormTest(TestCase):
    """Test cases for SessionForm"""

    def setUp(self):
        """Set up test data"""
        self.campaign = CampaignFactory()

    def test_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            "campaign": self.campaign.pk,
            "planning_notes": "Test planning notes",
            "session_notes": "Test session notes",
            "session_date": "2024-01-15",
        }
        form = SessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_campaign_required(self):
        """Test that campaign field is required"""
        form_data = {
            "campaign": "",
            "planning_notes": "Test planning notes",
            "session_notes": "Test session notes",
            "session_date": "2024-01-15",
        }
        form = SessionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("campaign", form.errors)

    def test_form_optional_fields(self):
        """Test that optional fields can be empty"""
        form_data = {
            "campaign": self.campaign.pk,
            "planning_notes": "",
            "session_notes": "",
            "session_date": "",
        }
        form = SessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_save(self):
        """Test that form can save a session"""
        form_data = {
            "campaign": self.campaign.pk,
            "planning_notes": "Test planning notes",
            "session_notes": "Test session notes",
            "session_date": "2024-01-15",
        }
        form = SessionForm(data=form_data)
        self.assertTrue(form.is_valid())

        session = form.save()
        self.assertEqual(session.campaign, self.campaign)
        self.assertEqual(session.planning_notes, "Test planning notes")
        self.assertEqual(session.session_notes, "Test session notes")
        self.assertEqual(str(session.session_date), "2024-01-15")

    def test_form_update_existing_session(self):
        """Test updating an existing session"""
        session = SessionFactory(campaign=self.campaign)
        form_data = {
            "campaign": self.campaign.pk,
            "planning_notes": "Updated planning notes",
            "session_notes": "Updated session notes",
            "session_date": "2024-02-15",
        }
        form = SessionForm(data=form_data, instance=session)
        self.assertTrue(form.is_valid())

        updated_session = form.save()
        self.assertEqual(updated_session.planning_notes, "Updated planning notes")
        self.assertEqual(updated_session.session_notes, "Updated session notes")
        self.assertEqual(str(updated_session.session_date), "2024-02-15")

    def test_form_date_field_format(self):
        """Test that date field accepts proper date format"""
        form_data = {
            "campaign": self.campaign.pk,
            "planning_notes": "Test planning notes",
            "session_notes": "Test session notes",
            "session_date": "2024-12-31",
        }
        form = SessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_date_format(self):
        """Test that invalid date format is rejected"""
        form_data = {
            "campaign": self.campaign.pk,
            "planning_notes": "Test planning notes",
            "session_notes": "Test session notes",
            "session_date": "invalid-date",
        }
        form = SessionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("session_date", form.errors)


class SessionViewTest(TestCase):
    """Test cases for session views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = UserFactory()
        self.campaign = CampaignFactory()
        self.session = SessionFactory(campaign=self.campaign)

    def test_session_list_view_requires_login(self):
        """Test that session list view requires login"""
        response = self.client.get(reverse("game_sessions:session_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_session_list_view_with_login(self):
        """Test session list view with authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("game_sessions:session_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session.campaign.title)

    def test_session_list_view_search(self):
        """Test session list view search functionality"""
        self.client.force_login(self.user)

        # Test search by campaign title
        response = self.client.get(
            reverse("game_sessions:session_list"), {"search": self.campaign.title}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session.campaign.title)

        # Test search by planning notes
        response = self.client.get(
            reverse("game_sessions:session_list"),
            {"search": self.session.planning_notes[:10]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session.campaign.title)

        # Test search by session notes
        response = self.client.get(
            reverse("game_sessions:session_list"),
            {"search": self.session.session_notes[:10]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session.campaign.title)

    def test_session_detail_view_requires_login(self):
        """Test that session detail view requires login"""
        response = self.client.get(
            reverse("game_sessions:session_detail", kwargs={"pk": self.session.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_session_detail_view_with_login(self):
        """Test session detail view with authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("game_sessions:session_detail", kwargs={"pk": self.session.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session.campaign.title)

        # Check for planning notes content - the template uses |linebreaks filter which converts \n to <br>
        # So we need to check for the content with HTML line breaks
        planning_notes_with_html_breaks = self.session.planning_notes.replace(
            "\n", "<br>"
        )
        self.assertContains(response, planning_notes_with_html_breaks)

        # Check for session notes content - the template uses |linebreaks filter which converts \n to <br>
        # So we need to check for the content with HTML line breaks
        session_notes_with_html_breaks = self.session.session_notes.replace(
            "\n", "<br>"
        )
        self.assertContains(response, session_notes_with_html_breaks)

    def test_session_detail_view_nonexistent(self):
        """Test session detail view with nonexistent session"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("game_sessions:session_detail", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)

    def test_session_create_view_requires_login(self):
        """Test that session create view requires login"""
        response = self.client.get(reverse("game_sessions:session_create"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_session_create_view_get(self):
        """Test session create view GET request"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("game_sessions:session_create"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], SessionForm)

    def test_session_create_view_post_valid(self):
        """Test session create view POST with valid data"""
        self.client.force_login(self.user)
        form_data = {
            "campaign": self.campaign.pk,
            "planning_notes": "New planning notes",
            "session_notes": "New session notes",
            "session_date": "2024-01-15",
        }
        response = self.client.post(reverse("game_sessions:session_create"), form_data)
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful creation

        # Check that session was created
        self.assertTrue(Session.objects.filter(campaign=self.campaign).exists())

    def test_session_create_view_post_invalid(self):
        """Test session create view POST with invalid data"""
        self.client.force_login(self.user)
        form_data = {
            "campaign": "",  # Invalid - empty campaign
            "planning_notes": "New planning notes",
            "session_notes": "New session notes",
            "session_date": "2024-01-15",
        }
        response = self.client.post(reverse("game_sessions:session_create"), form_data)
        self.assertEqual(response.status_code, 200)  # Form with errors
        self.assertContains(response, "This field is required")

    def test_session_update_view_requires_login(self):
        """Test that session update view requires login"""
        response = self.client.get(
            reverse("game_sessions:session_update", kwargs={"pk": self.session.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_session_update_view_get(self):
        """Test session update view GET request"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("game_sessions:session_update", kwargs={"pk": self.session.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], SessionForm)
        self.assertEqual(response.context["session"], self.session)

    def test_session_update_view_post_valid(self):
        """Test session update view POST with valid data"""
        self.client.force_login(self.user)
        form_data = {
            "campaign": self.campaign.pk,
            "planning_notes": "Updated planning notes",
            "session_notes": "Updated session notes",
            "session_date": "2024-02-15",
        }
        response = self.client.post(
            reverse("game_sessions:session_update", kwargs={"pk": self.session.pk}),
            form_data,
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful update

        # Check that session was updated
        updated_session = Session.objects.get(pk=self.session.pk)
        self.assertEqual(updated_session.planning_notes, "Updated planning notes")
        self.assertEqual(updated_session.session_notes, "Updated session notes")

    def test_session_update_view_post_invalid(self):
        """Test session update view POST with invalid data"""
        self.client.force_login(self.user)
        form_data = {
            "campaign": "",  # Invalid - empty campaign
            "planning_notes": "Updated planning notes",
            "session_notes": "Updated session notes",
            "session_date": "2024-02-15",
        }
        response = self.client.post(
            reverse("game_sessions:session_update", kwargs={"pk": self.session.pk}),
            form_data,
        )
        self.assertEqual(response.status_code, 200)  # Form with errors
        self.assertContains(response, "This field is required")

    def test_session_delete_view_requires_login(self):
        """Test that session delete view requires login"""
        response = self.client.get(
            reverse("game_sessions:session_delete", kwargs={"pk": self.session.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_session_delete_view_get(self):
        """Test session delete view GET request"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("game_sessions:session_delete", kwargs={"pk": self.session.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["session"], self.session)

    def test_session_delete_view_post(self):
        """Test session delete view POST request"""
        self.client.force_login(self.user)
        session_pk = self.session.pk
        response = self.client.post(
            reverse("game_sessions:session_delete", kwargs={"pk": session_pk})
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful deletion

        # Check that session was deleted
        self.assertFalse(Session.objects.filter(pk=session_pk).exists())

    def test_session_delete_view_nonexistent(self):
        """Test session delete view with nonexistent session"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("game_sessions:session_delete", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)

    def test_session_list_view_empty_search(self):
        """Test session list view with empty search query"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("game_sessions:session_list"), {"search": ""}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session.campaign.title)

    def test_session_list_view_no_results_search(self):
        """Test session list view with search that returns no results"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("game_sessions:session_list"), {"search": "nonexistent"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.session.campaign.title)

    def test_session_form_widgets(self):
        """Test that form widgets are properly configured"""
        form = SessionForm()

        # Check that campaign field has correct widget
        self.assertIsInstance(form.fields["campaign"].widget, forms.Select)

        # Check that textarea fields have correct widgets
        self.assertIsInstance(form.fields["planning_notes"].widget, forms.Textarea)
        self.assertIsInstance(form.fields["session_notes"].widget, forms.Textarea)

        # Check that date field has correct widget
        self.assertIsInstance(form.fields["session_date"].widget, forms.DateInput)

    def test_session_form_field_requirements(self):
        """Test that form field requirements are correctly set"""
        form = SessionForm()

        # Campaign should be required
        self.assertTrue(form.fields["campaign"].required)

        # Other fields should be optional
        self.assertFalse(form.fields["planning_notes"].required)
        self.assertFalse(form.fields["session_notes"].required)
        self.assertFalse(form.fields["session_date"].required)
