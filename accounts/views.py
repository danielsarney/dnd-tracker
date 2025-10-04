from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import qrcode
import io
import base64
from .models import User, TwoFactorCode
from .forms import UserRegistrationForm, LoginForm, TwoFactorForm, ProfileUpdateForm


def register_view(request):
    """User registration view"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("accounts:login")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """User login view with 2FA support"""
    if request.user.is_authenticated:
        return redirect("accounts:profile")  # Redirect to profile instead of home

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
                    # Redirect to 2FA setup if not enabled (mandatory)
                    request.session["user_id"] = user.id
                    return redirect("accounts:setup_2fa")
            else:
                pass  # Invalid credentials - no flash message
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def verify_2fa_view(request):
    """2FA verification view"""
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

            # Check TOTP code
            if user.verify_two_factor_code(code):
                login(request, user)
                del request.session["user_id"]
                return redirect("accounts:profile")
            else:
                pass  # Invalid verification code - no flash message
    else:
        form = TwoFactorForm()

    return render(request, "accounts/verify_2fa.html", {"form": form, "user": user})


def setup_2fa_view(request):
    """Setup 2FA for user (can be accessed without login for mandatory setup)"""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect("accounts:login")

    if request.method == "POST":
        if "verify_setup" in request.POST:
            code = request.POST.get("code")
            if user.verify_two_factor_code(code):
                user.two_factor_enabled = True
                user.save()
                login(request, user)
                del request.session["user_id"]
                return redirect("accounts:profile")
            else:
                pass  # Invalid verification code - no flash message

    # Always generate QR code for setup (skip initial screen)
    qr_url = user.get_two_factor_qr_code_url()
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
        {"qr_code": img_str, "secret": user.two_factor_secret, "user": user},
    )


@login_required
def profile_view(request):
    """User profile view with editable form"""
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
    """Logout view"""
    from django.contrib.auth import logout

    logout(request)
    return redirect("accounts:login")
