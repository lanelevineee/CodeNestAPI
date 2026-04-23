from django.urls import path
from .views import (
    UserProfile, PasswordResetRequestView, ConfirmPasswordResetView, SessionCounter,
    RegisterView, LoginView, LogoutView, TokenRefreshView,
    EmailVerificationView, ResendVerificationView, ChangePasswordView,
    ProfileUpdateView, UserSearchView
)

urlpatterns = [
    # Legacy endpoints
    path('', UserProfile.as_view(), name='user-list'),
    path('me/', UserProfile.as_view(), name='user-profile'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', ConfirmPasswordResetView.as_view(), name='password-reset-confirm'),
    path('visits-count/', SessionCounter.as_view(), name='visit_count'),
    
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Email verification
    path('verify-email/<uidb64>/<token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    
    # Password management
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Profile management
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    
    # User search
    path('search/', UserSearchView.as_view(), name='user-search'),
]
