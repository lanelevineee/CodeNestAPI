from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserProfile.as_view(), name='user-list'),
    path("me/", views.UserProfile.as_view(), name="user-profile"),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', views.ConfirmPasswordResetView.as_view(), name='password-reset-confirm'),
    path('visits-count/', views.SessionCounter.as_view(), name="visit_count")
]