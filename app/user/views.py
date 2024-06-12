"""
Views for the user API'
"""
from django.db import IntegrityError  # noqa
from django.http import Http404  # noqa
from rest_framework import generics, permissions
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.settings import api_settings
from django.contrib.auth import (  # noqa
    get_user_model,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, mixins, status  # noqa
from rest_framework.decorators import action  # noqa
from rest_framework.response import Response  # noqa
from user.serializers import (
    UserSerializer,
    UserProfileSerializer,
)
from core.models import UserProfile


class CreateUserView(generics.CreateAPIView):
    """Create a new User in the system"""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class ManageUserProfileView(generics.RetrieveUpdateAPIView):
    """Handle creating and updating authenticated user"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        """Retrieve and return authenticated"""
        return UserProfile.objects.get(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
