"""
Views for the user API'
"""
from rest_framework import generics, permissions
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.settings import api_settings
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import (
    UserSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new User in the system"""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user
