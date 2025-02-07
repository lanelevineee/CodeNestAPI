from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from .models import User, Profile
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

PASSWORD_TOKEN_GENERATOR = PasswordResetTokenGenerator()


class PasswordResetSerializer(Serializer):
    email = serializers.EmailField(max_length=255)
    
    
    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self, **kwargs):
        token = PasswordResetTokenGenerator().make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        current_site = get_current_site(self.context.get('request'))
        reset_link = f"http://{current_site.domain}/api/v1/users/reset-password/{uid}/{token}/"
        
        send_mail(
            subject="Password Reset",
            message=f"Click the link below to reset your password:\n\n{reset_link}",
            from_email=settings .EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False
        )

    
    
class ConfirmPasswordResetSerializer(Serializer):
    uid = serializers.CharField(help_text="Provide UID to confirm password reset")
    token = serializers.CharField(help_text="Provide Token to confirm password reset")
    old_password = serializers.CharField(
        style = {'input_type': 'password'},
        write_only = True,
        help_text="Enter Old Password"
    )
    new_password = serializers.CharField(
        min_length = 8,
        style = {'input_type': 'password'},
        write_only=True,
        help_text="Enter New Password."
    )
    confirm_password = serializers.CharField(
        min_length = 8,
        style = {'input_type': 'password'},
        write_only=True,
        help_text="Confirm New Password."
    )
    
    def validate(self, attrs):
        # Decode UID and get user
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid user ID")

        # Validate token
        if not PasswordResetTokenGenerator().check_token(self.user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired token")

        # Validate passwords match
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")

        return attrs

    def save(self, **kwargs):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()
        

class loggedInUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"