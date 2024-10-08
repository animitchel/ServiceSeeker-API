from django.http import Http404  # noqa
from rest_framework import generics, permissions
# from rest_framework.settings import api_settings
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, status  # noqa
from rest_framework.decorators import action  # noqa
from rest_framework.response import Response  # noqa
from user_profile.serializers import (
    UserProfileSerializer,
)
from core.models import UserProfile, ProviderProfile


class ManageUserProfileView(generics.CreateAPIView,
                            generics.RetrieveUpdateDestroyAPIView
                            ):
    """Handle creating and updating authenticated user"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        """Retrieve and return authenticated"""
        try:
            return UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            raise Http404("User not found, please create a new user-profile")

    def perform_create(self, serializer):
        """Create a new provider if it
        doesn't already exist for the user"""
        try:
            UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            user = self.request.user
            return serializer.save(user=user)

        # If the provider already exists, raise an error
        raise PermissionDenied(
            "Each user is allowed to have only "
            "one user-profile, and you already "
            "have an existing user-profile."
        )

    def perform_update(self, serializer):
        obj = self.get_object()
        user = self.request.user
        if not obj.user:
            raise PermissionDenied(
                "You do not have permission "
                "to update this object."
            )
        serializer.save(user=user)

    def delete(self, request, *args, **kwargs):
        """Delete the authenticated user's profile."""
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission "
                "to update this object."
            )
        try:
            """
            if you're deleting a user-profile,
            it also deletes your provider-profile,
            services and reviews attached to the services
            """
            ProviderProfile.objects.get(user=self.request.user).delete()
        except UserProfile.DoesNotExist:
            pass

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
