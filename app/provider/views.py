from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework import generics, permissions  # noqa
from rest_framework.exceptions import PermissionDenied
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

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from core import lists_of_choices
from .provider_helper_functions import get_max_ratings


class ProviderViewSet(viewsets.ModelViewSet):
    """View for manage provider APIS."""
    queryset = ProviderProfile.objects.all()
    serializer_class = ProviderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Create a new provider if it
        doesn't already exist for the user"""
        queryset = self.queryset
        user = self.request.user

        if queryset.filter(user=user).exists():
            # If the provider already exists, raise a validation error
            raise ValidationError(
                "You already have a provider profile. "
                "A user can only have one provider "
                "profile per user.")

        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update a provider profile"""
        instance = self.get_object()
        if serializer.is_valid():
            if instance.user != self.request.user:
                raise PermissionDenied(
                    "You do not have permission "
                    "to update this object."
                )

            serializer.save(user=self.request.user)
        else:
            raise ValidationError(serializer.errors)

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'Service Type',
                OpenApiTypes.STR,
                enum=lists_of_choices.SERVICE_TYPES_params,
                description='Name of '
                            'the service user is '
                            'interested in',
            ),
            OpenApiParameter(
                'Location',
                OpenApiTypes.STR,
                enum=lists_of_choices.LOCATION_params,
                description='Select the location '
                            'which the service is needed',
            ),
            OpenApiParameter(
                'Pricing',
                OpenApiTypes.FLOAT,
                description='The max price user is '
                            'willing to pay for '
                            'this service. Inputs '
                            'should be of type INT or '
                            'FLOAT',
            ),
            OpenApiParameter(
                'Top Rated',
                OpenApiTypes.INT,
                enum=[0, 1],  # this enum=[0, 1]
                # make sure only these to
                # values are accepted
                description='You have two '
                            'options, 1 for top '
                            'rated and 0 or None '
                            'for default options',
            ),
            OpenApiParameter(
                'availability',
                OpenApiTypes.STR,
                enum=lists_of_choices.AVAILABILITY_params,
                description='Availability of the service',
            ),
        ]
    )
)
class ServiceTypeViewSet(viewsets.ModelViewSet):
    """View for manage service type APIS."""
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieve all service types"""
        queryset = self.queryset

        service_type = self.request.query_params.get('Service Type')
        location = self.request.query_params.get('Location')
        pricing = self.request.query_params.get('Pricing', None)
        top_rated = self.request.query_params.get('Top Rated', 0)
        availability = self.request.query_params.get('availability')

        if service_type:
            queryset = queryset.filter(service_type=service_type)
        if location:
            queryset = queryset.filter(provider__location=location)
        if pricing:
            queryset = queryset.filter(pricing__lte=pricing)
        if top_rated:
            queryset = queryset.filter(
                user_reviews_rating__rating__gte=get_max_ratings(queryset))
        if availability:
            queryset = queryset.filter(availability=availability)

        if self.action == "create_review_rating":
            provider = ProviderProfile.objects.get(
                user=self.request.user
            )
            queryset = queryset.exclude(provider=provider)

        return queryset

    def perform_update(self, serializer):
        """Update a provider profile"""
        instance = self.get_object()
        if serializer.is_valid():
            if instance.provider.user != self.request.user:
                raise PermissionDenied(
                    "You do not have permission "
                    "to update this object."
                )

            serializer.save(user=self.request.user)
        else:
            raise ValidationError(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """Delete a provider profile"""
        instance = self.get_object()
        if instance.provider.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission "
                "to delete this object."
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        """Get all service types related
        to a specific authenticated provider
        currently logged in"""

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

        try:
            instance = self.get_object()
        except Http404:
            raise Http404("Object not found. "
                          "A provider cannot review themselves"
                          )

        serializer = self.get_serializer(
            data=request.data
        )

        if serializer.is_valid():

            try:
                Review.objects.get(user=self.request.user,
                                   service=instance
                                   )
            except Review.DoesNotExist:

                serializer.save(user=self.request.user,
                                service=instance
                                )
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )

            else:
                return Response(
                    "The object already exists. "
                    "User cant make a review to the "
                    "same service twice, "
                    "you can only retrieve, update or delete it",
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


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

    def perform_update(self, serializer):
        instance = self.get_object()
        if serializer.is_valid():
            if instance.user != self.request.user:
                raise PermissionDenied(
                    "You do not have permission "
                    "to update this object."
                )
            serializer.save(user=self.request.user)
        else:
            raise ValidationError(serializer.errors)

    def perform_destroy(self, instance):
        """Remove the review object from the database."""
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission "
                                   "to delete this object."
                                   )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
