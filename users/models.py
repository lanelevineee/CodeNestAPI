from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from .manager import UserBaseManager
from django.utils.translation import gettext_lazy as _
import random
from uuid import uuid4
import string


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True, blank=True, null=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName']
    objects = UserBaseManager()
    
    class Meta:
        verbose_name = 'USER ACCOUNTS'
        verbose_name_plural = "USERS ACCOUNTS"
    
    def __str__(self):
        return self.email or self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Upload a profile picture")
    bio = models.TextField(blank=True, default='')
    github = models.URLField(blank=True, default='')
    linkedin = models.URLField(blank=True, default='')
    is_moderator = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        
    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def set_user_names(sender, instance, created, **kwargs):
    """Sync firstName/lastName with first_name/last_name."""
    if created:
        # Generate username only if not provided
        if not instance.username:
            instance.username = f"#{uuid4().hex[:6].upper()}{random.choice(string.ascii_letters)}{random.randint(100, 99999)}"
            # Avoid recursive save by updating fields directly
            User.objects.filter(pk=instance.pk).update(
                username=instance.username,
                first_name=instance.firstName,
                last_name=instance.lastName
            )
    else:
        # Sync names on update
        if instance.first_name != instance.firstName or instance.last_name != instance.lastName:
            User.objects.filter(pk=instance.pk).update(
                first_name=instance.firstName,
                last_name=instance.lastName
            )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile instance for new users."""
    if created:
        Profile.objects.create(user=instance)