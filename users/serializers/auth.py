from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from ..models import User, Profile


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long."
    )
    confirm_password = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your password."
    )

    class Meta:
        model = User
        fields = ['email', 'firstName', 'lastName', 'password', 'confirm_password']

    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        # Remove confirm_password from attrs
        attrs.pop('confirm_password')

        # Validate password strength
        try:
            validate_password(attrs['password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            password=validated_data['password'],
            is_verified=False
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        attrs['user'] = user
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for verifying user email."""
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid verification link")

        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired verification token")

        if self.user.is_verified:
            raise serializers.ValidationError("Email already verified")

        return attrs

    def save(self, **kwargs):
        self.user.is_verified = True
        self.user.save()


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending verification email."""
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            # Don't reveal if email exists
            pass
        return value

    def save(self, **kwargs):
        if hasattr(self, 'user') and not self.user.is_verified:
            token = default_token_generator.make_token(self.user)
            uid = urlsafe_base64_encode(force_bytes(self.user.pk))
            current_site = get_current_site(self.context.get('request'))
            verification_link = f"http://{current_site.domain}/api/v1/auth/verify-email/{uid}/{token}/"

            send_mail(
                subject="Verify Your Email",
                message=f"Click the link below to verify your email:\n\n{verification_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.user.email],
                fail_silently=False
            )


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password (authenticated users)."""
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )
    new_password = serializers.CharField(
        min_length=8,
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )
    confirm_new_password = serializers.CharField(
        min_length=8,
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )

    def validate(self, attrs):
        user = self.context['request'].user

        # Check old password
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({"old_password": "Incorrect old password"})

        # Check if new passwords match
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "New passwords do not match"})

        # Validate new password strength
        try:
            validate_password(attrs['new_password'], user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    firstName = serializers.CharField(required=False)
    lastName = serializers.CharField(required=False)
    bio = serializers.CharField(required=False, allow_blank=True)
    github = serializers.URLField(required=False, allow_blank=True)
    linkedin = serializers.URLField(required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'bio', 'github', 'linkedin', 'avatar']

    def update(self, instance, validated_data):
        # Update user fields
        if 'firstName' in validated_data:
            instance.firstName = validated_data['firstName']
        if 'lastName' in validated_data:
            instance.lastName = validated_data['lastName']
        
        instance.save()

        # Update profile fields
        profile = instance.profile
        if 'bio' in validated_data:
            profile.bio = validated_data['bio']
        if 'github' in validated_data:
            profile.github = validated_data['github']
        if 'linkedin' in validated_data:
            profile.linkedin = validated_data['linkedin']
        if 'avatar' in validated_data:
            profile.avatar = validated_data['avatar']
        
        profile.save()

        return instance
