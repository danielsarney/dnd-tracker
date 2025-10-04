from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets
import pyotp
from datetime import timedelta


class User(AbstractUser):
    """Custom User model with 2FA support"""

    # 2FA fields
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)

    # Additional user fields
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def generate_two_factor_secret(self):
        """Generate a new 2FA secret key"""
        self.two_factor_secret = pyotp.random_base32()
        self.save()
        return self.two_factor_secret

    def get_two_factor_qr_code_url(self):
        """Get QR code URL for 2FA setup"""
        if not self.two_factor_secret:
            self.generate_two_factor_secret()

        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.provisioning_uri(name=self.email, issuer_name="D&D Tracker")

    def verify_two_factor_code(self, code):
        """Verify a 2FA code"""
        if not self.two_factor_secret:
            return False

        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(code, valid_window=1)


class TwoFactorCode(models.Model):
    """Model for storing temporary 2FA codes"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.code}"

    @classmethod
    def generate_code(cls, user):
        """Generate a new 2FA code for user"""
        # Clean up old codes
        cls.objects.filter(user=user, expires_at__lt=timezone.now()).delete()

        # Generate new code
        code = secrets.randbelow(900000) + 100000  # 6-digit code
        expires_at = timezone.now() + timedelta(minutes=10)

        return cls.objects.create(user=user, code=str(code), expires_at=expires_at)

    def is_valid(self):
        """Check if code is still valid"""
        return not self.used and self.expires_at > timezone.now()

    def mark_as_used(self):
        """Mark code as used"""
        self.used = True
        self.save()
