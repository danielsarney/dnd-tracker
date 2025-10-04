import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from accounts.models import TwoFactorCode

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances"""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.LazyFunction(lambda: "+1234567890")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    two_factor_enabled = False
    two_factor_secret = ""
    is_active = True
    is_staff = False
    is_superuser = False


class UserWith2FAFactory(UserFactory):
    """Factory for creating User instances with 2FA enabled"""

    two_factor_enabled = True
    two_factor_secret = factory.LazyFunction(lambda: "JBSWY3DPEHPK3PXP")


class SuperUserFactory(UserFactory):
    """Factory for creating superuser instances"""

    is_staff = True
    is_superuser = True
    email = factory.Sequence(lambda n: f"admin{n}@example.com")
    username = factory.Sequence(lambda n: f"admin{n}")


class TwoFactorCodeFactory(factory.django.DjangoModelFactory):
    """Factory for creating TwoFactorCode instances"""

    class Meta:
        model = TwoFactorCode

    user = factory.SubFactory(UserFactory)
    code = factory.Sequence(lambda n: f"{100000 + n:06d}")
    created_at = factory.LazyFunction(timezone.now)
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(minutes=10))
    used = False


class ExpiredTwoFactorCodeFactory(TwoFactorCodeFactory):
    """Factory for creating expired TwoFactorCode instances"""

    expires_at = factory.LazyFunction(lambda: timezone.now() - timedelta(minutes=1))


class UsedTwoFactorCodeFactory(TwoFactorCodeFactory):
    """Factory for creating used TwoFactorCode instances"""

    used = True
