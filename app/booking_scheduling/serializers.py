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
            'status',
            'details',
            'service_url',
            'user'
        ]
        read_only_fields = [
            'id', 'order_date',
            'service_url', 'user',
            'status',
        ]

    def get_service_url(self, obj) -> str:
        request = self.context.get('request')
        return reverse(
            'service:service-detail',
            kwargs={'pk': obj.service.pk}, request=request
        )
