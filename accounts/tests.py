from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile
from accounts.forms import CustomUserCreationForm, ProfileForm
from dnd_tracker.factories import UserFactory, UserWithProfileFactory


class UserFactoryTest(TestCase):
    """Test the UserFactory"""
    
    def test_user_factory_creates_user(self):
        user = UserFactory()
        self.assertIsInstance(user, User)
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.username)
        self.assertIsNotNone(user.email)
    
    def test_user_factory_creates_unique_users(self):
        user1 = UserFactory()
        user2 = UserFactory()
        self.assertNotEqual(user1.username, user2.username)
        self.assertNotEqual(user1.email, user2.email)

class UserWithProfileFactoryTest(TestCase):
    """Test the UserWithProfileFactory"""
    
    def test_user_with_profile_factory_creates_both(self):
        user = UserWithProfileFactory()
        self.assertIsInstance(user, User)
        self.assertIsInstance(user.profile, Profile)
        self.assertEqual(user.profile.user, user)


class ProfileModelTest(TestCase):
    """Test the Profile model"""
    
    def setUp(self):
        self.user = UserFactory()
        self.profile = self.user.profile
    
    def test_profile_creation(self):
        """Test that profile is automatically created when user is created"""
        self.assertIsInstance(self.profile, Profile)
        self.assertEqual(self.profile.user, self.user)
    
    def test_profile_str_method(self):
        """Test the __str__ method"""
        expected = f"{self.profile.display_name}'s Profile"
        self.assertEqual(str(self.profile), expected)
    
    def test_get_display_name(self):
        """Test get_display_name method"""
        self.assertEqual(self.profile.get_display_name(), self.profile.display_name)
    
    def test_get_display_name_fallback(self):
        """Test get_display_name falls back to username if display_name is empty"""
        self.profile.display_name = ""
        self.profile.save()
        self.assertEqual(self.profile.get_display_name(), self.user.username)


class CustomUserCreationFormTest(TestCase):
    """Test the CustomUserCreationForm"""
    
    def test_form_has_correct_fields(self):
        form = CustomUserCreationForm()
        expected_fields = ['username', 'email', 'password1', 'password2']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_form_validation_with_valid_data(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_validation_duplicate_username(self):
        # Create a user first
        UserFactory(username='testuser')
        
        form_data = {
            'username': 'testuser',  # Duplicate username
            'email': 'test2@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_form_validation_duplicate_email(self):
        # Create a user first
        UserFactory(email='test@example.com')
        
        form_data = {
            'username': 'testuser2',
            'email': 'test@example.com',  # Duplicate email
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class ProfileFormTest(TestCase):
    """Test the ProfileForm"""
    
    def setUp(self):
        self.user = UserWithProfileFactory()
        self.profile = self.user.profile
    
    def test_form_has_correct_fields(self):
        form = ProfileForm(instance=self.profile)
        expected_fields = ['display_name', 'email', 'avatar']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_form_validation_with_valid_data(self):
        form_data = {
            'display_name': 'New Display Name',
            'email': 'newemail@example.com'
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
    
    def test_form_validation_duplicate_display_name(self):
        # Create another user with a display name
        other_user = UserWithProfileFactory()
        other_user.profile.display_name = 'Taken Name'
        other_user.profile.save()
        
        form_data = {
            'display_name': 'Taken Name',  # Duplicate display name
            'email': 'newemail@example.com'
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('display_name', form.errors)
    
    def test_form_validation_duplicate_email(self):
        # Create another user with an email
        other_user = UserWithProfileFactory()
        other_user.profile.email = 'taken@example.com'
        other_user.profile.save()
        
        form_data = {
            'display_name': 'New Display Name',
            'email': 'taken@example.com'  # Duplicate email
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class AccountsViewsTest(TestCase):
    """Test the accounts views"""
    
    def setUp(self):
        self.client = Client()
        self.user = UserWithProfileFactory()
        self.user.set_password('testpass123')
        self.user.save()
    
    def test_signup_view_get(self):
        """Test signup view GET request"""
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertContains(response, 'Join the Adventure')
    
    def test_signup_view_post_success(self):
        """Test successful signup"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(reverse('accounts:signup'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check that user was created
        new_user = User.objects.get(username='newuser')
        self.assertIsNotNone(new_user)
        self.assertIsNotNone(new_user.profile)
        self.assertEqual(new_user.profile.email, 'newuser@example.com')
    
    def test_signup_view_post_duplicate_username(self):
        """Test signup with duplicate username"""
        form_data = {
            'username': self.user.username,  # Duplicate username
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(reverse('accounts:signup'), form_data)
        self.assertEqual(response.status_code, 200)  # Form errors, no redirect
        self.assertContains(response, 'Username is already taken')
    
    def test_signup_view_post_duplicate_email(self):
        """Test signup with duplicate email"""
        form_data = {
            'username': 'newuser',
            'email': self.user.profile.email,  # Duplicate email
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(reverse('accounts:signup'), form_data)
        self.assertEqual(response.status_code, 200)  # Form errors, no redirect
        self.assertContains(response, 'Email address is already registered')
    
    def test_profile_view_get(self):
        """Test profile view GET request"""
        self.client.login(username=self.user.username, password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, 'Your Profile')
    
    def test_profile_view_post_success(self):
        """Test successful profile update"""
        self.client.login(username=self.user.username, password='testpass123')
        form_data = {
            'display_name': 'Updated Display Name',
            'email': 'updated@example.com'
        }
        response = self.client.post(reverse('accounts:profile'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check that profile was updated
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.display_name, 'Updated Display Name')
        self.assertEqual(self.user.profile.email, 'updated@example.com')
    
    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication"""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class AccountsURLsTest(TestCase):
    """Test the accounts URLs"""
    
    def test_signup_url(self):
        """Test signup URL"""
        url = reverse('accounts:signup')
        self.assertEqual(url, '/accounts/signup/')
    
    def test_profile_url(self):
        """Test profile URL"""
        url = reverse('accounts:profile')
        self.assertEqual(url, '/accounts/profile/')