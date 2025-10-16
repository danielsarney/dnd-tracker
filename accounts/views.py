"""
User Account Views for D&D Tracker

This module contains all the view functions for user authentication and
account management. It handles user registration, login with two-factor
authentication (2FA), profile management, and logout functionality.

Key Features:
- User registration with email-based authentication
- Login with mandatory 2FA setup
- 2FA verification using TOTP codes
- QR code generation for authenticator app setup
- User profile management
- Secure logout handling
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import qrcode
import io
import base64
from .models import User, TwoFactorCode
from .forms import UserRegistrationForm, LoginForm, TwoFactorForm, ProfileUpdateForm


def register_view(request):
    """
    Handle user registration.

    This view processes user registration forms and creates new user accounts.
    After successful registration, users are redirected to the login page.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered registration page or redirect to login
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("accounts:login")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """
    Handle user login with 2FA support.

    This view processes login attempts and handles the 2FA workflow:
    1. Authenticate user with email and password
    2. If 2FA is enabled, generate backup code and redirect to verification
    3. If 2FA is not enabled, redirect to mandatory 2FA setup
    4. If authentication fails, show error message

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered login page, 2FA verification, or profile redirect
    """
    # Redirect authenticated users to profile
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # Authenticate user with email as username
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.two_factor_enabled:
                    # User has 2FA enabled - generate backup code and verify TOTP
                    TwoFactorCode.generate_code(user)
                    request.session["user_id"] = user.id
                    return redirect("accounts:verify_2fa")
                else:
                    # User needs to set up 2FA (mandatory for security)
                    request.session["user_id"] = user.id
                    return redirect("accounts:setup_2fa")
            else:
                form.add_error(None, "Invalid email or password")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def verify_2fa_view(request):
    """
    Handle 2FA verification for users with 2FA enabled.

    This view verifies TOTP codes from authenticator apps. Users must
    provide a valid 6-digit code to complete the login process.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered 2FA verification page or redirect to profile
    """
    # Check if user ID is stored in session (from login process)
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect("accounts:login")

    if request.method == "POST":
        form = TwoFactorForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]

            # Verify TOTP code from authenticator app
            if user.verify_two_factor_code(code):
                login(request, user)
                del request.session["user_id"]
                return redirect("accounts:profile")
            else:
                form.add_error(None, "Invalid verification code")
    else:
        form = TwoFactorForm()

    return render(request, "accounts/verify_2fa.html", {"form": form, "user": user})


def setup_2fa_view(request):
    """
    Handle 2FA setup for new users.

    This view generates QR codes for authenticator app setup and verifies
    the initial TOTP code to enable 2FA. 2FA setup is mandatory for all users.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered 2FA setup page with QR code or redirect to profile
    """
    # Check if user is logged in normally
    if request.user.is_authenticated:
        user = request.user
    else:
        # Check if user is in session (for mandatory setup after login)
        user_id = request.session.get("user_id")
        if not user_id:
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(request.get_full_path())

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect("accounts:login")

    if request.method == "POST":
        form = TwoFactorForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            # Verify the TOTP code to confirm authenticator app setup
            if user.verify_two_factor_code(code):
                user.two_factor_enabled = True
                user.save()
                login(request, user)
                if "user_id" in request.session:
                    del request.session["user_id"]
                return redirect("accounts:profile")
            else:
                form.add_error(None, "Invalid verification code")
    else:
        form = TwoFactorForm()

    # Generate QR code for authenticator app setup
    qr_url = user.get_two_factor_qr_code_url()
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)

    # Convert QR code to base64 for display in template
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer)
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return render(
        request,
        "accounts/setup_2fa.html",
        {
            "qr_code": img_str,
            "secret": user.two_factor_secret,
            "user": user,
            "form": form,
        },
    )


@login_required
def profile_view(request):
    """
    Display and handle user profile updates.

    This view shows the user's profile information and allows them to
    update their account details including email, phone number, etc.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered profile page with user information and form
    """
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(
        request, "accounts/profile.html", {"form": form, "user": request.user}
    )


def logout_view(request):
    """
    Handle user logout.

    This view logs out the current user and redirects them to the login page.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Redirect to login page
    """
    from django.contrib.auth import logout

    logout(request)
    return redirect("accounts:login")
