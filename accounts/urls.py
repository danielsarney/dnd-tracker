from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication URLs
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    # 2FA URLs
    path("verify-2fa/", views.verify_2fa_view, name="verify_2fa"),
    path("setup-2fa/", views.setup_2fa_view, name="setup_2fa"),
    # Profile URLs
    path("profile/", views.profile_view, name="profile"),
]
