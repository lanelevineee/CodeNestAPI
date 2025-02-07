from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from rest_framework import serializers, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import User, Profile
from django.conf import settings
from .serializer import PasswordResetSerializer, ConfirmPasswordResetSerializer, loggedInUserSerializer
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage



PASSWORD_TOKEN_GENERATOR = PasswordResetTokenGenerator()

class UserProfile(APIView):
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'message':'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(id=request.user.id)
        serializer = loggedInUserSerializer(user)
        return Response({'message':f"user {serializer.data['username']}. Your email is {serializer.data['email']}"}, status=status.HTTP_200_OK)



class PasswordResetRequestView(APIView):
    serializer_class = PasswordResetSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            reset_link = serializer.save()
            return Response({"message": "Password reset link sent if email exists"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ConfirmPasswordResetView(APIView):
    serializer_class = ConfirmPasswordResetSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class SessionCounter(APIView):
    def get(self, request, *args, **kwargs):
        visits = request.session.get('visits', 0) + 1
        request.session['visits'] = visits
        print(request.session.items())
        return Response({'visits': visits}, status=status.HTTP_200_OK, content_type="text/html")