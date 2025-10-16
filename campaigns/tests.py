from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from dnd_tracker.factories import UserFactory, CampaignFactory
from campaigns.models import Campaign
from campaigns.forms import CampaignForm

User = get_user_model()


class CampaignModelTest(TestCase):
    """Test cases for Campaign model"""

    def setUp(self):
        """Set up test data"""
        self.campaign = CampaignFactory()

    def test_campaign_creation(self):
        """Test that a campaign can be created with all fields"""
        self.assertIsInstance(self.campaign, Campaign)
        self.assertTrue(self.campaign.title)
        self.assertTrue(self.campaign.description)
        self.assertTrue(self.campaign.introduction)
        self.assertTrue(self.campaign.character_requirements)

    def test_campaign_str_representation(self):
        """Test the string representation of Campaign"""
        expected = self.campaign.title
        self.assertEqual(str(self.campaign), expected)

    def test_campaign_title_required(self):
        """Test that title is required"""
        with self.assertRaises(ValidationError):
            Campaign.objects.create(
                title="",
                description="Test description",
                introduction="Test introduction",
                character_requirements="Test requirements",
            )

    def test_campaign_optional_fields(self):
        """Test that optional fields can be empty"""
        campaign = Campaign.objects.create(
            title="Test Campaign",
            description="",
            introduction="",
            character_requirements="",
        )
        self.assertEqual(campaign.title, "Test Campaign")
        self.assertEqual(campaign.description, "")
        self.assertEqual(campaign.introduction, "")
        self.assertEqual(campaign.character_requirements, "")

    def test_campaign_ordering(self):
        """Test that campaigns are ordered by title"""
        # Clear existing campaigns from setUp
        Campaign.objects.all().delete()

        campaign_a = CampaignFactory(title="Alpha Campaign")
        campaign_b = CampaignFactory(title="Beta Campaign")
        campaign_c = CampaignFactory(title="Charlie Campaign")

        campaigns = Campaign.objects.all()
        self.assertEqual(campaigns[0], campaign_a)
        self.assertEqual(campaigns[1], campaign_b)
        self.assertEqual(campaigns[2], campaign_c)


class CampaignFormTest(TestCase):
    """Test cases for CampaignForm"""

    def test_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            "title": "Test Campaign",
            "description": "Test description",
            "introduction": "Test introduction",
            "character_requirements": "Test requirements",
        }
        form = CampaignForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_title_required(self):
        """Test that title field is required"""
        form_data = {
            "title": "",
            "description": "Test description",
            "introduction": "Test introduction",
            "character_requirements": "Test requirements",
        }
        form = CampaignForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_optional_fields(self):
        """Test that optional fields can be empty"""
        form_data = {
            "title": "Test Campaign",
            "description": "",
            "introduction": "",
            "character_requirements": "",
        }
        form = CampaignForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_save(self):
        """Test that form can save a campaign"""
        form_data = {
            "title": "Test Campaign",
            "description": "Test description",
            "introduction": "Test introduction",
            "character_requirements": "Test requirements",
        }
        form = CampaignForm(data=form_data)
        self.assertTrue(form.is_valid())

        campaign = form.save()
        self.assertEqual(campaign.title, "Test Campaign")
        self.assertEqual(campaign.description, "Test description")
        self.assertEqual(campaign.introduction, "Test introduction")
        self.assertEqual(campaign.character_requirements, "Test requirements")

    def test_form_update_existing_campaign(self):
        """Test updating an existing campaign"""
        campaign = CampaignFactory()
        form_data = {
            "title": "Updated Campaign",
            "description": "Updated description",
            "introduction": "Updated introduction",
            "character_requirements": "Updated requirements",
        }
        form = CampaignForm(data=form_data, instance=campaign)
        self.assertTrue(form.is_valid())

        updated_campaign = form.save()
        self.assertEqual(updated_campaign.title, "Updated Campaign")
        self.assertEqual(updated_campaign.description, "Updated description")
        self.assertEqual(updated_campaign.introduction, "Updated introduction")
        self.assertEqual(
            updated_campaign.character_requirements, "Updated requirements"
        )


class CampaignViewTest(TestCase):
    """Test cases for campaign views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = UserFactory()
        self.campaign = CampaignFactory()

    def test_campaign_list_view_requires_login(self):
        """Test that campaign list view requires login"""
        response = self.client.get(reverse("campaigns:campaign_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_campaign_list_view_with_login(self):
        """Test campaign list view with authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("campaigns:campaign_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.title)

    def test_campaign_list_view_search(self):
        """Test campaign list view search functionality"""
        self.client.force_login(self.user)

        # Test search by title
        response = self.client.get(
            reverse("campaigns:campaign_list"), {"search": self.campaign.title}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.title)

        # Test search by description
        response = self.client.get(
            reverse("campaigns:campaign_list"),
            {"search": self.campaign.description[:10]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.title)

    def test_campaign_detail_view_requires_login(self):
        """Test that campaign detail view requires login"""
        response = self.client.get(
            reverse("campaigns:campaign_detail", kwargs={"pk": self.campaign.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_campaign_detail_view_with_login(self):
        """Test campaign detail view with authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("campaigns:campaign_detail", kwargs={"pk": self.campaign.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.title)
        # Check for description content - just check that description section exists
        self.assertContains(response, "Description")
        # Check for some part of the description text
        description_words = self.campaign.description.split()[:5]  # First 5 words
        description_sample = " ".join(description_words)
        self.assertContains(response, description_sample)

    def test_campaign_detail_view_nonexistent(self):
        """Test campaign detail view with nonexistent campaign"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("campaigns:campaign_detail", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)

    def test_campaign_create_view_requires_login(self):
        """Test that campaign create view requires login"""
        response = self.client.get(reverse("campaigns:campaign_create"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_campaign_create_view_get(self):
        """Test campaign create view GET request"""
        self.client.force_login(self.user)
        response = self.client.get(reverse("campaigns:campaign_create"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], CampaignForm)

    def test_campaign_create_view_post_valid(self):
        """Test campaign create view POST with valid data"""
        self.client.force_login(self.user)
        form_data = {
            "title": "New Campaign",
            "description": "New description",
            "introduction": "New introduction",
            "character_requirements": "New requirements",
        }
        response = self.client.post(reverse("campaigns:campaign_create"), form_data)
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful creation

        # Check that campaign was created
        self.assertTrue(Campaign.objects.filter(title="New Campaign").exists())

    def test_campaign_create_view_post_invalid(self):
        """Test campaign create view POST with invalid data"""
        self.client.force_login(self.user)
        form_data = {
            "title": "",  # Invalid - empty title
            "description": "New description",
            "introduction": "New introduction",
            "character_requirements": "New requirements",
        }
        response = self.client.post(reverse("campaigns:campaign_create"), form_data)
        self.assertEqual(response.status_code, 200)  # Form with errors
        self.assertContains(response, "This field is required")

    def test_campaign_update_view_requires_login(self):
        """Test that campaign update view requires login"""
        response = self.client.get(
            reverse("campaigns:campaign_update", kwargs={"pk": self.campaign.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_campaign_update_view_get(self):
        """Test campaign update view GET request"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("campaigns:campaign_update", kwargs={"pk": self.campaign.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], CampaignForm)
        self.assertEqual(response.context["campaign"], self.campaign)

    def test_campaign_update_view_post_valid(self):
        """Test campaign update view POST with valid data"""
        self.client.force_login(self.user)
        form_data = {
            "title": "Updated Campaign",
            "description": "Updated description",
            "introduction": "Updated introduction",
            "character_requirements": "Updated requirements",
        }
        response = self.client.post(
            reverse("campaigns:campaign_update", kwargs={"pk": self.campaign.pk}),
            form_data,
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful update

        # Check that campaign was updated
        updated_campaign = Campaign.objects.get(pk=self.campaign.pk)
        self.assertEqual(updated_campaign.title, "Updated Campaign")

    def test_campaign_update_view_post_invalid(self):
        """Test campaign update view POST with invalid data"""
        self.client.force_login(self.user)
        form_data = {
            "title": "",  # Invalid - empty title
            "description": "Updated description",
            "introduction": "Updated introduction",
            "character_requirements": "Updated requirements",
        }
        response = self.client.post(
            reverse("campaigns:campaign_update", kwargs={"pk": self.campaign.pk}),
            form_data,
        )
        self.assertEqual(response.status_code, 200)  # Form with errors
        self.assertContains(response, "This field is required")

    def test_campaign_delete_view_requires_login(self):
        """Test that campaign delete view requires login"""
        response = self.client.get(
            reverse("campaigns:campaign_delete", kwargs={"pk": self.campaign.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_campaign_delete_view_get(self):
        """Test campaign delete view GET request"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("campaigns:campaign_delete", kwargs={"pk": self.campaign.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["campaign"], self.campaign)

    def test_campaign_delete_view_post(self):
        """Test campaign delete view POST request"""
        self.client.force_login(self.user)
        campaign_pk = self.campaign.pk
        response = self.client.post(
            reverse("campaigns:campaign_delete", kwargs={"pk": campaign_pk})
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful deletion

        # Check that campaign was deleted
        self.assertFalse(Campaign.objects.filter(pk=campaign_pk).exists())

    def test_campaign_delete_view_nonexistent(self):
        """Test campaign delete view with nonexistent campaign"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("campaigns:campaign_delete", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)
