from django.contrib import admin
from .models import User, Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'firstName', 'lastName', 'is_verified', 'is_staff', 'date_joined']
    list_filter = ['is_verified', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['email', 'username', 'firstName', 'lastName']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_moderator', 'date_joined']
    list_filter = ['is_moderator']
    search_fields = ['user__email', 'user__username', 'bio']
    ordering = ['-date_joined']