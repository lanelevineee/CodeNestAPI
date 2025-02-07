from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from .manager import UserBaseManager
from django.utils.translation import gettext_lazy as _
import random
from uuid import uuid4
import string
class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName']
    objects = UserBaseManager()
    
    class Meta:
        verbose_name = 'USER ACCOUNTS'
        verbose_name_plural = "USERS ACCOUNTS"
    
    # def save(self, force_insert = ..., force_update = ..., using = ..., update_fields = ...):
    #     self.first_name = self.firstName
    #     self.last_name = self.lastName
    #     return super().save(force_insert, force_update, using, update_fields)
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add other fields as needed
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Upload a profile picture")
    bio = models.TextField()
    github = models.URLField()
    linkedin = models.URLField()
    is_moderator = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        
    def __str__(self):
        return self.user.username


@receiver(sender=User, signal=post_save)
def set_default_username(sender, instance, created, **kwargs):
    if created:
        generateUsername = f"#{uuid4().hex[:6].upper()}{random.choice(string.ascii_letters)}{random.randint(100, 99999)}"
        instance.username = generateUsername
        instance.save()
        
        
@receiver(sender=User, signal=post_save)
def create_profile(sender, instance, created, **kwargs):
    if created:
        instance.first_name = instance.firstName
        instance.last_name = instance.lastName
        instance.save()
        Profile.objects.create(user=instance).save()
        instance.save()