"""
User Account Models for D&D Tracker

This module defines the custom User model and related authentication models
for the D&D Tracker application. It extends Django's AbstractUser to include
two-factor authentication (2FA) support using TOTP (Time-based One-Time Password).

Key Features:
- Custom User model with email as username
- Two-factor authentication using pyotp library
- Temporary 2FA codes for backup authentication
- User profile information storage
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets
import pyotp
from datetime import timedelta


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    This model provides enhanced user authentication with two-factor authentication
    support. Users log in using their email address instead of username, and can
    optionally enable 2FA for additional security.

    Attributes:
        two_factor_enabled: Boolean flag indicating if 2FA is enabled for this user
        two_factor_secret: Base32-encoded secret key for TOTP generation
        email: User's email address (used as username)
        phone_number: Optional phone number for contact
        created_at: Timestamp when user account was created
        updated_at: Timestamp when user account was last modified
    """

    # Two-Factor Authentication fields
    two_factor_enabled = models.BooleanField(
        default=False,
        help_text="Whether two-factor authentication is enabled for this user",
    )
    two_factor_secret = models.CharField(
        max_length=32,
        blank=True,
        help_text="Base32-encoded secret key for TOTP generation",
    )

    # Additional user profile fields
    email = models.EmailField(
        unique=True, help_text="User's email address (used as username for login)"
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        help_text="Optional phone number for contact purposes",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the user account was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the user account was last modified"
    )

    # Django authentication configuration
    USERNAME_FIELD = "email"  # Use email instead of username for login
    REQUIRED_FIELDS = ["username"]  # Username still required for Django admin

    def __str__(self):
        """String representation of the user"""
        return self.email

    def generate_two_factor_secret(self):
        """
        Generate a new 2FA secret key for the user.

        This method creates a new base32-encoded secret key using pyotp's
        random_base32() function and saves it to the user's profile.

        Returns:
            str: The newly generated secret key
        """
        self.two_factor_secret = pyotp.random_base32()
        self.save()
        return self.two_factor_secret

    def get_two_factor_qr_code_url(self):
        """
        Get QR code URL for 2FA setup in authenticator apps.

        This method generates a provisioning URI that can be used to create
        a QR code for setting up the user's authenticator app (like Google
        Authenticator or Authy).

        Returns:
            str: Provisioning URI for QR code generation
        """
        if not self.two_factor_secret:
            self.generate_two_factor_secret()

        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.provisioning_uri(name=self.email, issuer_name="D&D Tracker")

    def verify_two_factor_code(self, code):
        """
        Verify a 2FA code entered by the user.

        This method validates the TOTP code provided by the user against
        the stored secret key. It uses a valid_window of 1 to account for
        slight time differences between the authenticator app and server.

        Args:
            code (str): The 6-digit code from the user's authenticator app

        Returns:
            bool: True if the code is valid, False otherwise
        """
        if not self.two_factor_secret:
            return False

        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(code, valid_window=1)


class TwoFactorCode(models.Model):
    """
    Model for storing temporary 2FA backup codes.

    This model stores one-time backup codes that can be used as an alternative
    to TOTP codes when users can't access their authenticator app. These codes
    are generated on-demand and expire after a short period for security.

    Attributes:
        user: Foreign key to the User who owns this code
        code: 6-digit numeric code for authentication
        created_at: Timestamp when the code was generated
        expires_at: Timestamp when the code expires (typically 10 minutes)
        used: Boolean flag indicating if the code has been used
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="The user this backup code belongs to"
    )
    code = models.CharField(max_length=6, help_text="6-digit numeric backup code")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the code was generated"
    )
    expires_at = models.DateTimeField(help_text="Timestamp when the code expires")
    used = models.BooleanField(
        default=False, help_text="Whether this code has been used for authentication"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """String representation of the backup code"""
        return f"{self.user.email} - {self.code}"

    @classmethod
    def generate_code(cls, user):
        """
        Generate a new backup 2FA code for a user.

        This class method creates a new 6-digit backup code for the specified
        user. It automatically cleans up expired codes for that user before
        generating a new one to prevent code accumulation.

        Args:
            user (User): The user to generate a backup code for

        Returns:
            TwoFactorCode: The newly created backup code instance
        """
        # Clean up old expired codes for this user
        cls.objects.filter(user=user, expires_at__lt=timezone.now()).delete()

        # Generate a new 6-digit code (100000 to 999999)
        code = secrets.randbelow(900000) + 100000
        expires_at = timezone.now() + timedelta(minutes=10)

        return cls.objects.create(user=user, code=str(code), expires_at=expires_at)

    def is_valid(self):
        """
        Check if this backup code is still valid for use.

        A code is valid if it hasn't been used and hasn't expired.

        Returns:
            bool: True if the code can be used, False otherwise
        """
        return not self.used and self.expires_at > timezone.now()

    def mark_as_used(self):
        """
        Mark this backup code as used to prevent reuse.

        This method should be called immediately after a successful
        authentication using this code to prevent replay attacks.
        """
        self.used = True
        self.save()
