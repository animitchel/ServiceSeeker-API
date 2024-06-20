from django.http import Http404
from rest_framework import generics, permissions  # noqa
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.settings import api_settings
# from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from provider.serializers import (
    ProviderSerializer,
    ServiceTypeSerializer,
    ReviewSerializer,
)
from core.models import ProviderProfile, ServiceType, Review


class ProviderViewSet(viewsets.ModelViewSet):
    """View for manage provider APIS."""
    queryset = ProviderProfile.objects.all()
    serializer_class = ProviderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Create a new provider"""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Retrieve the provider objects for the authenticated user"""
        if self.action == "list":
            return self.queryset
        else:
            return self.queryset.filter(user=self.request.user)


class ServiceTypeViewSet(viewsets.ModelViewSet):
    """View for manage service type APIS."""
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieve all service types"""
        if self.action == "list":
            return self.queryset
        else:
            try:
                provider = ProviderProfile.objects.get(user=self.request.user)
            except ProviderProfile.DoesNotExist:
                raise Http404("Provider does not exist")
            else:
                return ServiceType.objects.filter(provider=provider)

    def get_serializer_class(self):
        if self.action == "create_review_rating":
            return ReviewSerializer
        elif self.action == "get_service_types":
            return ServiceTypeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new servicetype"""
        try:
            provider = ProviderProfile.objects.get(
                user=self.request.user
            )

        except ProviderProfile.DoesNotExist:
            raise Http404("Provider does not exist. "
                          "Users have to register as a provider, "
                          "to be allowed to add their services."
                          "Please register as a provider first."
                          )

        serializer.save(provider=provider)

    @action(detail=False, methods=['GET'], url_path='provider-service')
    def get_service_types(self, request, pk=None):
        """Get all service types related to a specific provider"""

        try:
            provider = ProviderProfile.objects.get(
                user=self.request.user
            )
        except ProviderProfile.DoesNotExist:
            return Response(
                'ProviderProfile matching query does not exist.',
                status=status.HTTP_404_NOT_FOUND)

        queryset = ServiceType.objects.filter(provider=provider)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='review-rating')
    def create_review_rating(self, request, pk=None):
        """Create a new rating and review for service"""
        service = self.get_object()
        try:

            user_pro = ProviderProfile.objects.get(
                user=self.request.user
            )

            user_provider_service = ServiceType.objects.filter(
                provider=user_pro
            )

            for obj in user_provider_service:
                if obj == service:
                    return Response(
                        'A provider cannot review themselves',
                        status=status.HTTP_400_BAD_REQUEST
                    )

        except ProviderProfile.DoesNotExist:
            pass

        finally:
            review, created = Review.objects.get_or_create(
                user=self.request.user, service=service
            )
            if created:
                serializer = self.get_serializer(
                    review, data=request.data
                )

                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        serializer.data,
                        status=status.HTTP_200_OK
                    )
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    "The object already exists. "
                    "User cant make a review to the "
                    "same service twice, "
                    "you can only retrieve, update or delete it",
                    status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """View for manage review APIS."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieve the reviewed objects."""
        if self.action == 'list':
            return self.queryset
        else:
            return self.queryset.filter(user=self.request.user)
