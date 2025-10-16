"""
User Account Forms for D&D Tracker

This module contains all Django forms for user authentication and account
management. It includes forms for user registration, login, 2FA verification,
profile updates, and password changes.

Key Features:
- Custom user registration with email validation
- Login form with remember me functionality
- 2FA verification form with code validation
- Profile update form with uniqueness checks
- Password change form with current password verification
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """
    Custom user registration form extending Django's UserCreationForm.

    This form handles user registration with additional fields for email,
    first name, last name, and phone number. It includes custom validation
    to ensure email and username uniqueness.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter your email"}
        ),
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter your first name"}
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter your last name"}
        ),
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your phone number (optional)",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        """Initialize form with Bootstrap styling for all fields."""
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Choose a username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm password"}
        )

    def clean_email(self):
        """
        Validate that the email address is unique.

        Returns:
            str: The cleaned email address

        Raises:
            ValidationError: If email already exists
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        """
        Validate that the username is unique.

        Returns:
            str: The cleaned username

        Raises:
            ValidationError: If username already exists
        """
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username


class LoginForm(forms.Form):
    """
    Custom login form for user authentication.

    This form handles user login with email and password fields, plus
    an optional "remember me" checkbox for extended sessions.
    """

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter your email"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter your password"}
        )
    )
    remember_me = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )


class TwoFactorForm(forms.Form):
    """
    2FA verification form for TOTP code entry.

    This form handles the entry of 6-digit TOTP codes from authenticator
    apps during the login process or 2FA setup.
    """

    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control text-center",
                "placeholder": "000000",
                "maxlength": "6",
                "pattern": "[0-9]{6}",
                "style": "font-size: 1.5rem; letter-spacing: 0.5rem;",
            }
        ),
    )

    def clean_code(self):
        """
        Validate that the code is a 6-digit number.

        Returns:
            str: The cleaned code

        Raises:
            ValidationError: If code is not valid
        """
        code = self.cleaned_data.get("code")
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError("Please enter a valid 6-digit code.")
        return code


class ProfileUpdateForm(forms.ModelForm):
    """
    User profile update form for editing account information.

    This form allows users to update their profile information including
    username, name, email, and phone number with uniqueness validation.
    """

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone_number"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        """
        Validate that the email address is unique (excluding current user).

        Returns:
            str: The cleaned email address

        Raises:
            ValidationError: If email already exists for another user
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        """
        Validate that the username is unique (excluding current user).

        Returns:
            str: The cleaned username

        Raises:
            ValidationError: If username already exists for another user
        """
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username


class PasswordChangeForm(forms.Form):
    """
    Password change form for updating user passwords.

    This form handles password changes with current password verification
    and new password confirmation.
    """

    current_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter current password"}
        )
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter new password"}
        )
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm new password"}
        )
    )

    def __init__(self, user, *args, **kwargs):
        """Initialize form with the current user for password verification."""
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        """
        Validate that the current password is correct.

        Returns:
            str: The cleaned current password

        Raises:
            ValidationError: If current password is incorrect
        """
        current_password = self.cleaned_data.get("current_password")
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect.")
        return current_password

    def clean(self):
        """
        Validate that the new passwords match.

        Returns:
            dict: The cleaned form data

        Raises:
            ValidationError: If new passwords do not match
        """
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("New passwords do not match.")

        return cleaned_data
