from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from .models import User, Profile
from .serializers.auth import (
    RegisterSerializer, LoginSerializer, EmailVerificationSerializer,
    ResendVerificationSerializer, ChangePasswordSerializer, ProfileUpdateSerializer
)
from .serializer import LoggedInUserSerializer


class UserProfile(APIView):
    """API View for user profile operations."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = LoggedInUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = LoggedInUserSerializer(
            instance=request.user,
            data=request.data,
            partial=False
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        serializer = LoggedInUserSerializer(
            instance=request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """API View for user registration."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Send verification email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            verification_link = f"http://{current_site.domain}/api/v1/auth/verify-email/{uid}/{token}/"

            send_mail(
                subject="Verify Your Email",
                message=f"Welcome {user.firstName}! Click the link below to verify your email:\n\n{verification_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'firstName': user.firstName,
                    'lastName': user.lastName,
                    'is_verified': user.is_verified
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """API View for user login."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': f'Welcome back, {user.firstName}!',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'firstName': user.firstName,
                    'lastName': user.lastName,
                    'is_verified': user.is_verified
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """API View for user logout (blacklist refresh token)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TokenRefreshView(APIView):
    """API View for refreshing access token."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Invalid or expired refresh token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmailVerificationView(APIView):
    """API View for verifying user email."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Email verified successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    """API View for resending verification email."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ResendVerificationSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Verification email sent if email exists and is not verified'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """API View for changing password (authenticated users)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileUpdateView(APIView):
    """API View for updating user profile."""
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = ProfileUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=False
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'username': request.user.username,
                    'firstName': request.user.firstName,
                    'lastName': request.user.lastName,
                    'bio': request.user.profile.bio,
                    'github': request.user.profile.github,
                    'linkedin': request.user.profile.linkedin,
                    'avatar': request.build_absolute_uri(request.user.profile.avatar.url) if request.user.profile.avatar else None
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        serializer = ProfileUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'username': request.user.username,
                    'firstName': request.user.firstName,
                    'lastName': request.user.lastName,
                    'bio': request.user.profile.bio,
                    'github': request.user.profile.github,
                    'linkedin': request.user.profile.linkedin,
                    'avatar': request.build_absolute_uri(request.user.profile.avatar.url) if request.user.profile.avatar else None
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSearchView(APIView):
    """API View for searching users."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return Response({
                'message': 'Search query is required',
                'users': []
            }, status=status.HTTP_200_OK)
        
        users = User.objects.filter(
            Q(firstName__icontains=query) |
            Q(lastName__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query)
        ).exclude(pk=request.user.pk if request.user.is_authenticated else None)[:20]
        
        return Response({
            'count': users.count(),
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'firstName': user.firstName,
                    'lastName': user.lastName,
                    'avatar': request.build_absolute_uri(user.profile.avatar.url) if user.profile.avatar else None
                }
                for user in users
            ]
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """Request a password reset link via email."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        from .serializer import PasswordResetSerializer
        serializer = PasswordResetSerializer(
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
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        from .serializer import ConfirmPasswordResetSerializer
        serializer = ConfirmPasswordResetSerializer(
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
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        visits = request.session.get('visits', 0) + 1
        request.session['visits'] = visits
        return Response({'visits': visits}, status=status.HTTP_200_OK)
