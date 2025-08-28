from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def avatar_upload_path(instance, filename):
    """Generate upload path for avatar: avatars/username/filename"""
    return f'avatars/{instance.user.username}/{filename}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=80, unique=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    
    def __str__(self):
        return f"{self.display_name}'s Profile"
    
    def get_display_name(self):
        return self.display_name or self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile with email from user if available
        email = getattr(instance, 'email', f'{instance.username}@example.com')
        Profile.objects.create(
            user=instance, 
            display_name=instance.username,
            email=email
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
