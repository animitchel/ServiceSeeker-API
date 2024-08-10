from django.http import Http404
from rest_framework.exceptions import ValidationError, PermissionDenied  # noqa
from rest_framework import generics, permissions  # noqa
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.settings import api_settings
# from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from booking_scheduling.serializers import (
    ServiceOrderSerializer
)
from core.models import (
    ProviderProfile, ServiceType, ServiceOrder)

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


class ServiceOrderViewSet(viewsets.ViewSet):
    queryset = ServiceOrder.objects.all()
    serializer_class = ServiceOrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #
    #     return ServiceOrder.objects.none()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'id',
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                description=""
                            "A unique integer value identifying "
                            "the service-type for this request"
            )
        ]
    )
    @action(detail=True, methods=['POST'], url_path='request-A-service')
    def create_request_for_service(self, request, pk):
        request_serializer = ServiceOrderSerializer(data=request.data)
        if request_serializer.is_valid():

            try:
                service = ServiceType.objects.get(id=pk)
            except ServiceType.DoesNotExist:
                raise Http404('Service Type does not exist')

            provider = ProviderProfile.objects.get(services=service)

            if ServiceOrder.objects.filter(
                    user=request.user, service=service).exists():
                raise PermissionDenied(
                    "Your request to the service as already being processed."
                )

            if provider.user != request.user:

                request_serializer.save(user=request.user, service=service)
                return Response(
                    request_serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                raise PermissionDenied(
                    "You do not have permission "
                    "to request this service."
                )

        else:
            return Response(
                request_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
