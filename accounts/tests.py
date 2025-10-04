from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
import pyotp
from accounts.models import TwoFactorCode
from accounts.forms import UserRegistrationForm, LoginForm, TwoFactorForm
from dnd_tracker.factories import (
    UserFactory,
    UserWith2FAFactory,
    TwoFactorCodeFactory,
    ExpiredTwoFactorCodeFactory,
    UsedTwoFactorCodeFactory,
)

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the User model"""

    def setUp(self):
        self.user = UserFactory()

    def test_user_creation(self):
        """Test basic user creation"""
        self.assertTrue(self.user.email.endswith("@example.com"))
        self.assertTrue(self.user.username.startswith("user"))
        self.assertTrue(self.user.check_password("testpass123"))
        self.assertFalse(self.user.two_factor_enabled)
        self.assertEqual(self.user.two_factor_secret, "")

    def test_user_str_representation(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), self.user.email)

    def test_generate_two_factor_secret(self):
        """Test 2FA secret generation"""
        secret = self.user.generate_two_factor_secret()
        self.assertIsNotNone(secret)
        self.assertEqual(len(secret), 32)
        self.user.refresh_from_db()
        self.assertEqual(self.user.two_factor_secret, secret)

    def test_get_two_factor_qr_code_url(self):
        """Test QR code URL generation"""
        qr_url = self.user.get_two_factor_qr_code_url()
        self.assertIn("otpauth://totp/", qr_url)
        self.assertIn(self.user.email.replace("@", "%40"), qr_url)
        self.assertIn("D%26D%20Tracker", qr_url)  # URL encoded version

    def test_verify_two_factor_code_valid(self):
        """Test valid 2FA code verification"""
        self.user.two_factor_secret = "JBSWY3DPEHPK3PXP"
        self.user.save()

        totp = pyotp.TOTP(self.user.two_factor_secret)
        valid_code = totp.now()

        self.assertTrue(self.user.verify_two_factor_code(valid_code))

    def test_verify_two_factor_code_invalid(self):
        """Test invalid 2FA code verification"""
        self.user.two_factor_secret = "JBSWY3DPEHPK3PXP"
        self.user.save()

        invalid_code = "123456"
        self.assertFalse(self.user.verify_two_factor_code(invalid_code))

    def test_verify_two_factor_code_no_secret(self):
        """Test 2FA verification when no secret is set"""
        self.assertFalse(self.user.verify_two_factor_code("123456"))


class TwoFactorCodeModelTest(TestCase):
    """Test cases for the TwoFactorCode model"""

    def setUp(self):
        self.user = UserFactory()

    def test_two_factor_code_creation(self):
        """Test basic TwoFactorCode creation"""
        code = TwoFactorCodeFactory(user=self.user)
        self.assertEqual(code.user, self.user)
        self.assertEqual(len(code.code), 6)
        self.assertTrue(code.code.isdigit())
        self.assertFalse(code.used)
        self.assertTrue(code.is_valid())

    def test_generate_code_class_method(self):
        """Test the generate_code class method"""
        code = TwoFactorCode.generate_code(self.user)
        self.assertEqual(code.user, self.user)
        self.assertEqual(len(code.code), 6)
        self.assertTrue(code.code.isdigit())
        self.assertFalse(code.used)
        self.assertTrue(code.is_valid())

    def test_is_valid_fresh_code(self):
        """Test is_valid for fresh codes"""
        code = TwoFactorCodeFactory(user=self.user)
        self.assertTrue(code.is_valid())

    def test_is_valid_expired_code(self):
        """Test is_valid for expired codes"""
        code = ExpiredTwoFactorCodeFactory(user=self.user)
        self.assertFalse(code.is_valid())

    def test_is_valid_used_code(self):
        """Test is_valid for used codes"""
        code = UsedTwoFactorCodeFactory(user=self.user)
        self.assertFalse(code.is_valid())

    def test_mark_as_used(self):
        """Test marking code as used"""
        code = TwoFactorCodeFactory(user=self.user)
        self.assertFalse(code.used)
        code.mark_as_used()
        self.assertTrue(code.used)

    def test_str_representation(self):
        """Test string representation"""
        code = TwoFactorCodeFactory(user=self.user)
        expected = f"{self.user.email} - {code.code}"
        self.assertEqual(str(code), expected)


class UserRegistrationFormTest(TestCase):
    """Test cases for UserRegistrationForm"""

    def test_valid_registration_form(self):
        """Test valid form submission"""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_email_uniqueness_validation(self):
        """Test email uniqueness validation"""
        UserFactory(email="existing@example.com")

        form_data = {
            "username": "testuser",
            "email": "existing@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_username_uniqueness_validation(self):
        """Test username uniqueness validation"""
        UserFactory(username="existinguser")

        form_data = {
            "username": "existinguser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


class LoginFormTest(TestCase):
    """Test cases for LoginForm"""

    def test_valid_login_form(self):
        """Test valid login form"""
        form_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "remember_me": True,
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email_format(self):
        """Test invalid email format"""
        form_data = {
            "email": "invalid-email",
            "password": "testpass123",
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class TwoFactorFormTest(TestCase):
    """Test cases for TwoFactorForm"""

    def test_valid_6_digit_code(self):
        """Test valid 6-digit code"""
        form_data = {"code": "123456"}
        form = TwoFactorForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_short_code(self):
        """Test invalid short code"""
        form_data = {"code": "12345"}
        form = TwoFactorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)

    def test_invalid_long_code(self):
        """Test invalid long code"""
        form_data = {"code": "1234567"}
        form = TwoFactorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)

    def test_invalid_non_numeric_code(self):
        """Test invalid non-numeric code"""
        form_data = {"code": "abc123"}
        form = TwoFactorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)


class LoginViewTest(TestCase):
    """Test cases for login view"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.login_url = reverse("accounts:login")

    def test_login_page_loads(self):
        """Test login page loads correctly"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome Back")

    def test_successful_login_without_2fa(self):
        """Test successful login without 2FA"""
        response = self.client.post(
            self.login_url,
            {
                "email": self.user.email,
                "password": "testpass123",
            },
        )
        # Should redirect to home, which then redirects to login
        self.assertEqual(response.status_code, 302)

    def test_successful_login_with_2fa(self):
        """Test login redirects to 2FA when enabled"""
        user_with_2fa = UserWith2FAFactory()
        response = self.client.post(
            self.login_url,
            {
                "email": user_with_2fa.email,
                "password": "testpass123",
            },
        )
        self.assertRedirects(response, reverse("accounts:verify_2fa"))

    def test_invalid_login_credentials(self):
        """Test invalid login credentials"""
        response = self.client.post(
            self.login_url,
            {
                "email": self.user.email,
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")

    def test_authenticated_user_redirect(self):
        """Test authenticated user is redirected"""
        self.client.force_login(self.user)
        response = self.client.get(self.login_url)
        # Should redirect to home, which then redirects to login
        self.assertEqual(response.status_code, 302)


class RegisterViewTest(TestCase):
    """Test cases for register view"""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse("accounts:register")

    def test_register_page_loads(self):
        """Test register page loads correctly"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Join the Adventure")

    def test_successful_registration(self):
        """Test successful user registration"""
        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "phone_number": "+1234567890",
                "password1": "complexpass123",
                "password2": "complexpass123",
            },
        )
        self.assertRedirects(response, reverse("accounts:login"))

        # Check user was created
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())


class Verify2FAViewTest(TestCase):
    """Test cases for 2FA verification view"""

    def setUp(self):
        self.client = Client()
        self.user = UserWith2FAFactory()
        self.verify_url = reverse("accounts:verify_2fa")

    def test_verify_2fa_page_loads(self):
        """Test 2FA verification page loads"""
        # Simulate login session
        session = self.client.session
        session["user_id"] = self.user.id
        session.save()

        response = self.client.get(self.verify_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Two-Factor Authentication")

    def test_verify_2fa_without_session(self):
        """Test 2FA verification without session"""
        response = self.client.get(self.verify_url)
        self.assertRedirects(response, reverse("accounts:login"))

    def test_successful_2fa_verification(self):
        """Test successful 2FA verification"""
        session = self.client.session
        session["user_id"] = self.user.id
        session.save()

        # Generate valid TOTP code
        totp = pyotp.TOTP(self.user.two_factor_secret)
        valid_code = totp.now()

        response = self.client.post(
            self.verify_url,
            {
                "code": valid_code,
            },
        )
        # Should redirect to home, which then redirects to login
        self.assertEqual(response.status_code, 302)

    def test_invalid_2fa_code(self):
        """Test invalid 2FA code"""
        session = self.client.session
        session["user_id"] = self.user.id
        session.save()

        response = self.client.post(
            self.verify_url,
            {
                "code": "123456",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid verification code")


class Setup2FAViewTest(TestCase):
    """Test cases for 2FA setup view"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.setup_url = reverse("accounts:setup_2fa")

    def test_setup_2fa_page_loads(self):
        """Test 2FA setup page loads"""
        self.client.force_login(self.user)
        response = self.client.get(self.setup_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Setup Two-Factor Authentication")

    def test_setup_2fa_requires_login(self):
        """Test 2FA setup requires login"""
        response = self.client.get(self.setup_url)
        self.assertRedirects(response, f"/accounts/login/?next={self.setup_url}")

    def test_enable_2fa_generates_qr_code(self):
        """Test enabling 2FA generates QR code"""
        self.client.force_login(self.user)
        response = self.client.post(
            self.setup_url,
            {
                "enable_2fa": "1",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Setup Instructions")
        self.assertContains(response, "data:image/png;base64,")

    def test_verify_2fa_setup(self):
        """Test verifying 2FA setup"""
        self.client.force_login(self.user)

        # First enable 2FA to get QR code
        self.client.post(self.setup_url, {"enable_2fa": "1"})

        # Generate valid TOTP code
        self.user.refresh_from_db()
        totp = pyotp.TOTP(self.user.two_factor_secret)
        valid_code = totp.now()

        response = self.client.post(
            self.setup_url,
            {
                "verify_setup": "1",
                "code": valid_code,
            },
        )
        self.assertRedirects(response, reverse("accounts:profile"))

        # Check 2FA is enabled
        self.user.refresh_from_db()
        self.assertTrue(self.user.two_factor_enabled)


class ProfileViewTest(TestCase):
    """Test cases for profile view"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.profile_url = reverse("accounts:profile")

    def test_profile_page_loads(self):
        """Test profile page loads"""
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profile Settings")

    def test_profile_requires_login(self):
        """Test profile requires login"""
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f"/accounts/login/?next={self.profile_url}")

    def test_profile_shows_user_info(self):
        """Test profile shows user information"""
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)


class LogoutViewTest(TestCase):
    """Test cases for logout view"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.logout_url = reverse("accounts:logout")

    def test_logout_redirects_to_login(self):
        """Test logout redirects to login page"""
        self.client.force_login(self.user)
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, reverse("accounts:login"))

    def test_logout_clears_session(self):
        """Test logout clears user session"""
        self.client.force_login(self.user)
        self.assertTrue(self.user.is_authenticated)

        self.client.post(self.logout_url)
        response = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(
            response, f'/accounts/login/?next={reverse("accounts:profile")}'
        )
