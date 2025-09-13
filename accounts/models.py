from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
import cloudinary
import re


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=80, unique=True)
    email = models.EmailField(unique=True)
    avatar_url = models.URLField(max_length=500, null=True, blank=True, help_text="URL to user's avatar image")
    
    def get_display_name(self):
        return self.display_name or self.user.username
    
    def __str__(self):
        return f"{self.get_display_name()}'s Profile"
    
    @property
    def avatar(self):
        """Property to maintain backward compatibility with existing code"""
        return self.avatar_url
    
    def delete_old_avatar(self, old_avatar_url):
        """Safely delete old avatar from Cloudinary or local storage"""
        if not old_avatar_url:
            return
            
        try:
            if not settings.DEBUG and hasattr(settings, 'CLOUDINARY_STORAGE'):
                # Production: Delete from Cloudinary
                if 'cloudinary.com' in old_avatar_url:
                    # Extract public_id from Cloudinary URL
                    # Format: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/folder/filename.jpg
                    url_parts = old_avatar_url.split('/')
                    if 'upload' in url_parts:
                        upload_index = url_parts.index('upload')
                        if upload_index + 1 < len(url_parts):
                            # Get everything after 'upload' and before any version number
                            public_id_parts = url_parts[upload_index + 2:]
                            # Remove version number if present (starts with 'v')
                            if public_id_parts and public_id_parts[0].startswith('v'):
                                public_id_parts = public_id_parts[1:]
                            public_id = '/'.join(public_id_parts)
                            # Remove file extension
                            public_id = re.sub(r'\.[^.]*$', '', public_id)
                            
                            try:
                                cloudinary.uploader.destroy(public_id)
                            except Exception as e:
                                # Log error but don't fail the save operation
                                if settings.DEBUG:
                                    print(f"Failed to delete Cloudinary image {public_id}: {e}")
                                # In production, you might want to log this to a monitoring service
            else:
                # Development: Delete local file
                import os
                if old_avatar_url.startswith('/media/'):
                    file_path = settings.MEDIA_ROOT / old_avatar_url.replace('/media/', '')
                    if os.path.exists(file_path):
                        os.remove(file_path)
        except Exception as e:
            # Log error but don't fail the save operation
            # In production, you might want to use proper logging here
            if settings.DEBUG:
                print(f"Failed to delete old avatar: {e}")
            # You could also log to a file or external service in production


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


@receiver(pre_save, sender=Profile)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    """Delete old avatar when profile is updated with new avatar"""
    if instance.pk:  # Only for existing profiles, not new ones
        try:
            old_profile = Profile.objects.get(pk=instance.pk)
            if old_profile.avatar_url != instance.avatar_url and instance.avatar_url:
                # New avatar uploaded, delete the old one
                instance.delete_old_avatar(old_profile.avatar_url)
        except Profile.DoesNotExist:
            pass  # Profile doesn't exist yet


@receiver(models.signals.pre_delete, sender=Profile)
def delete_avatar_on_profile_delete(sender, instance, **kwargs):
    """Delete avatar when profile is deleted"""
    if instance.avatar_url:
        instance.delete_old_avatar(instance.avatar_url)
