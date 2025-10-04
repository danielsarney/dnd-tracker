from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import qrcode
import io
import base64
from .models import User, TwoFactorCode
from .forms import UserRegistrationForm, LoginForm, TwoFactorForm


def register_view(request):
    """User registration view"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("accounts:login")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """User login view with 2FA support"""
    if request.user.is_authenticated:
        return redirect("home")  # Redirect to your main app

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.two_factor_enabled:
                    # Generate 2FA code and redirect to verification
                    TwoFactorCode.generate_code(user)
                    request.session["user_id"] = user.id
                    return redirect("accounts:verify_2fa")
                else:
                    # Login directly if 2FA is not enabled
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect("home")
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def verify_2fa_view(request):
    """2FA verification view"""
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Please log in first.")
        return redirect("accounts:login")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("accounts:login")

    if request.method == "POST":
        form = TwoFactorForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]

            # Check TOTP code
            if user.verify_two_factor_code(code):
                login(request, user)
                del request.session["user_id"]
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("home")
            else:
                messages.error(request, "Invalid verification code.")
    else:
        form = TwoFactorForm()

    return render(request, "accounts/verify_2fa.html", {"form": form, "user": user})


@login_required
def setup_2fa_view(request):
    """Setup 2FA for authenticated user"""
    if request.method == "POST":
        if "enable_2fa" in request.POST:
            # Generate QR code for setup
            qr_url = request.user.get_two_factor_qr_code_url()
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer)
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return render(
                request,
                "accounts/setup_2fa.html",
                {"qr_code": img_str, "secret": request.user.two_factor_secret},
            )

        elif "verify_setup" in request.POST:
            code = request.POST.get("code")
            if request.user.verify_two_factor_code(code):
                request.user.two_factor_enabled = True
                request.user.save()
                messages.success(request, "2FA has been enabled successfully!")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Invalid verification code.")

    return render(request, "accounts/setup_2fa.html")


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, "accounts/profile.html", {"user": request.user})


def logout_view(request):
    """Logout view"""
    from django.contrib.auth import logout

    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("accounts:login")
