from rest_framework import serializers
from rest_framework.reverse import reverse
from core.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    services_url = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'rating',
            'review_text',
            'services_url', 'user',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at',
                            'updated_at',
                            'services_url',
                            'user',
                            ]

    def get_services_url(self, obj) -> str:
        request = self.context.get('request')
        return reverse(
            'service:service-detail',
            kwargs={'pk': obj.service.pk},
            request=request
        )
