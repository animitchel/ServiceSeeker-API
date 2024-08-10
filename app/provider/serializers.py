from core.models import ProviderProfile

# from django.utils.translation import gettext as _

from rest_framework import serializers
from rest_framework.reverse import reverse


class ProviderSerializer(serializers.ModelSerializer):
    services_url = serializers.SerializerMethodField()

    class Meta:
        model = ProviderProfile
        # exclude = ('average_rating',)
        fields = [
            'id',
            'location',
            'profile_picture',
            'bio',
            'experience_years',
            'certifications',
            'certifications_documents',
            'average_rating',
            'phone_number',
            'services_url',
            'user',
            'created_at', 'updated_at',
        ]

        read_only_fields = [
            'created_at', 'updated_at',
            'user', 'id', 'average_rating',
            'services_url']
        extra_kwargs = {'user': {'required': True}}

    def get_services_url(self, obj) -> list[str]:
        request = self.context.get('request')
        services = obj.services.all()
        return [
            reverse(
                'service:service-detail',
                kwargs={'pk': service.pk},
                request=request) for service in services
        ]
