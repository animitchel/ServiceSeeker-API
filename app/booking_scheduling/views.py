from django.http import Http404
from rest_framework.exceptions import ValidationError, PermissionDenied  # noqa
from rest_framework import generics, permissions  # noqa
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.settings import api_settings
# from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from booking_scheduling.serializers import (
    ServiceOrderSerializer,
    ServiceOrderSerializerForProvider
)
from core.models import (
    ProviderProfile, ServiceType, ServiceOrder)

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


class ServiceOrderViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """View to retrieve, list and manage Service Orders"""
    queryset = ServiceOrder.objects.all()
    serializer_class = ServiceOrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter queryset based on the
        current user and no appointment
        """
        return self.queryset.filter(
            user=self.request.user,
            is_appointment=False
        )

    def get_serializer_class(self):
        action = [
            'completed_appointment',
            'response_to_request_for_service',
            'approved_service_order'
        ]
        serializer = self.serializer_class
        if self.action in action:
            serializer = ServiceOrderSerializerForProvider
        else:
            serializer = ServiceOrderSerializer
        return serializer

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
        """
        For a user to request a service order
        and possibly create an appointment for that service
        """
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
                    "Your earlier request to the service is currently pending."
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'id',
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                description=""
                            "A unique integer value identifying "
                            "the service-order for this request"
            )
        ]
    )
    @action(detail=True, methods=['POST'],
            url_path='response-to-service-request')
    def response_to_request_for_service(self, request, pk):
        """A particular service provider can
        respond to a service order request"""
        serializer = ServiceOrderSerializerForProvider(
            data=request.data
        )
        try:
            service_order = ServiceOrder.objects.exclude(
                status='completed').get(id=pk)
        except ServiceOrder.DoesNotExist:
            raise Http404('Service Order does not exist')

        requested_service_provider = ProviderProfile.objects.get(
            services=service_order.service
        )
        auth_provider = ProviderProfile.objects.get(user=request.user)

        if requested_service_provider == auth_provider:
            if serializer.is_valid():

                appointment_status = serializer.validated_data['status']

                if appointment_status == 'canceled':

                    service_order.delete()
                    return Response(status.HTTP_204_NO_CONTENT)
                elif (appointment_status == 'completed' and
                      service_order.status != 'pending'):
                    service_order.status = appointment_status
                    service_order.save()
                    return Response(
                        ServiceOrderSerializerForProvider(service_order).data,
                        status=status.HTTP_201_CREATED
                    )
                elif (appointment_status == 'approved' and
                      service_order.status != 'approved'):
                    service_order.status = appointment_status
                    service_order.is_appointment = True
                    service_order.save()

                    return Response(
                        ServiceOrderSerializerForProvider(service_order).data,
                        status=status.HTTP_201_CREATED
                    )

                else:
                    raise PermissionDenied(
                        "Service Order is already approved. "
                        "Or still has not been approved."
                    )

            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST
                                )
        else:
            raise PermissionDenied(
                "You do not have permission to perform this action"
            )

    @action(detail=False, methods=['GET'],
            url_path='service-orders-appointment')
    def approved_service_order(self, request, pk=None):
        """The user can see all their approved service order request"""
        queryset = ServiceOrder.objects.all().filter(
            user=request.user, is_appointment=True,
            status='approved'
        )
        serializer = ServiceOrderSerializerForProvider(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'],
            url_path='completed-service-order-appointment')
    def completed_appointment(self, request, pk=None):
        """
        The user can see all their completed
        service order appointment request
        """
        queryset = ServiceOrder.objects.all().filter(
            user=request.user, status='completed'
        )
        serializer = ServiceOrderSerializerForProvider(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
