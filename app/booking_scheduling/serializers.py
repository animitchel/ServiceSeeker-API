from core.models import ServiceOrder
from rest_framework import serializers
from rest_framework.reverse import reverse


class ServiceOrderSerializer(serializers.ModelSerializer):
    service_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceOrder

        fields = [
            'id',
            'order_date',
            'details',
            'appointment_date',
            'is_appointment',
            'service_url',
            'user'
        ]
        read_only_fields = [
            'id', 'order_date',
            'service_url', 'user',
            'is_appointment',
        ]

        extra_kwargs = {'appointment_date': {
            'required': True,
        }}

    def get_service_url(self, obj) -> str:
        request = self.context.get('request')
        return reverse(
            'service:service-detail',
            kwargs={'pk': obj.service.pk}, request=request
        )


class ServiceOrderSerializerForProvider(ServiceOrderSerializer):
    class Meta(ServiceOrderSerializer.Meta):
        fields = ServiceOrderSerializer.Meta.fields + ['status']
        read_only_fields = (
                ServiceOrderSerializer.Meta.read_only_fields +
                ['details', 'appointment_date']
        )
        extra_kwargs = {'status': {'required': True}}
