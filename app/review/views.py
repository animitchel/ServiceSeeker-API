from django.http import Http404
from rest_framework.exceptions import ValidationError, PermissionDenied  # noqa
from rest_framework import generics, permissions  # noqa
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.settings import api_settings
# from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from review.serializers import (
    ReviewSerializer,
)
from core.models import Review, ServiceType, ProviderProfile
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


class ReviewViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """
        View for manage review APIS.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer, *args, **kwargs):
        """Update the review object in the database"""
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission "
                "to update this object."
            )
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance, *args, **kwargs):
        """Remove the review object from the database."""
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission "
                                   "to delete this object."
                                   )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'id',
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                description=""
                            "A unique integer value identifying "
                            "the service about to be review"
            )
        ]
    )
    @action(detail=True, methods=['POST'], url_path='review-rating')
    def create_review_rating(self, request, pk):
        """Create a review for service"""

        try:
            instance = ServiceType.objects.get(id=pk)
        except ServiceType.DoesNotExist:
            raise Http404("Service type does not exist")

        try:
            provider = ProviderProfile.objects.get(
                user=self.request.user
            )
        except ProviderProfile.DoesNotExist:
            raise Http404("Provider does not exist")

        try:
            ServiceType.objects.get(id=instance.id, provider=provider)
        except ServiceType.DoesNotExist:

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
                        status=status.HTTP_201_CREATED
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
        else:
            raise PermissionDenied("You do not have permission. "
                                   "A provider cannot review themselves"
                                   )
