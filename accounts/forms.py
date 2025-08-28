from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Create a password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm your password'
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists in Profile model
            if Profile.objects.filter(email=email).exists():
                raise forms.ValidationError('This email address is already registered.')
            # Also check if email already exists in User model
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('This email address is already registered.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check if username already exists in Profile model
            if Profile.objects.filter(display_name=username).exists():
                raise forms.ValidationError('This username is already taken.')
        return username


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'email', 'avatar']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your display name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def clean_display_name(self):
        display_name = self.cleaned_data['display_name']
        if Profile.objects.filter(display_name=display_name).exclude(user=self.instance.user).exists():
            raise forms.ValidationError('This display name is already taken.')
        return display_name
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if Profile.objects.filter(email=email).exclude(user=self.instance.user).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email
