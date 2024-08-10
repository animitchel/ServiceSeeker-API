from rest_framework.exceptions import ValidationError, PermissionDenied  # noqa
from rest_framework import generics, permissions  # noqa
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.settings import api_settings
# from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from provider.serializers import (
    ProviderSerializer,
)
from core.models import ProviderProfile, ServiceType, UserProfile, ServiceOrder
from booking_scheduling.serializers import ServiceOrderSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    """View for manage provider APIS."""
    queryset = ProviderProfile.objects.all()
    serializer_class = ProviderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer """
        if self.action == "get_service_requests":
            return ServiceOrderSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new provider if it
        doesn't already exist for the user"""
        queryset = self.queryset
        user = self.request.user
        try:
            UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            raise PermissionDenied(
                "You do not have permission "
                "to create this object. "
                "Create user-profile before you can "
                "create a provider profile"
            )
        if queryset.filter(user=user).exists():
            # If the provider already exists, raise a validation error
            raise PermissionDenied(
                "You already have a provider profile. "
                "A user can only have one provider "
                "profile per user.")

        serializer.save(user=user)

    def perform_update(self, serializer, *args, **kwargs):
        """Update a provider profile"""
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission "
                "to update this object."
            )

        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Delete a provider profile"""
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission "
                "to delete this object."
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            url_path='provider-service-requests'
            )
    def get_service_requests(self, request, pk=None):

        provider = ProviderProfile.objects.get(user=self.request.user)
        services = ServiceType.objects.filter(provider=provider)
        service_request = ServiceOrder.objects.filter(service__in=services)

        serializer = ServiceOrderSerializer(service_request, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
