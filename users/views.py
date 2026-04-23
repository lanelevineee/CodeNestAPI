from django.urls import reverse_lazy, reverse
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import User, Profile
from django.conf import settings
from .serializer import PasswordResetSerializer, ConfirmPasswordResetSerializer, LoggedInUserSerializer
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site


PASSWORD_TOKEN_GENERATOR = PasswordResetTokenGenerator()


class UserProfile(APIView):
    """Get the currently logged-in user's profile information."""

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'message': 'Unauthorized'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = LoggedInUserSerializer(request.user)
        return Response(
            {
                'message': f"user {serializer.data['username']}. Your email is {serializer.data['email']}",
                'user': serializer.data
            },
            status=status.HTTP_200_OK
        )


class PasswordResetRequestView(APIView):
    """Request a password reset link via email."""
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password reset link sent if email exists"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmPasswordResetView(APIView):
    """Confirm and complete password reset with new password."""
    serializer_class = ConfirmPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password reset successful"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionCounter(APIView):
    """Track and return the number of visits in the current session."""

    def get(self, request, *args, **kwargs):
        visits = request.session.get('visits', 0) + 1
        request.session['visits'] = visits
        return Response({'visits': visits}, status=status.HTTP_200_OK)