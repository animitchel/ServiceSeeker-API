from core.models import ProviderProfile, ServiceType, Review
# from django.contrib.auth import (
#     get_user_model,
# )

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

    def get_services_url(self, obj):
        request = self.context.get('request')
        services = obj.services.all()
        return [
            reverse(
                'provider:service-detail',
                kwargs={'pk': service.pk},
                request=request) for service in services
        ]


class ServiceTypeSerializer(serializers.ModelSerializer):
    provider_url = serializers.SerializerMethodField()
    user_review_rating_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceType
        fields = ['id',
                  'service_type', 'description',
                  'pricing', 'availability',
                  'user_review_rating_url',
                  'provider_url',
                  'created_at', 'updated_at',
                  ]
        read_only_fields = ['id', 'created_at', 'updated_at',
                            'provider_url', 'user_review_rating_url'
                            ]
        extra_kwargs = {'service_type': {'required': True},
                        'description': {'required': True},
                        'pricing': {'required': True},
                        'availability': {'required': True}
                        }

    def get_provider_url(self, obj):
        request = self.context.get('request')
        return reverse(
            'provider:profile-detail',
            kwargs={'pk': obj.provider.pk},
            request=request
        )

    def get_user_review_rating_url(self, obj):
        request = self.context.get('request')
        reviews = obj.user_reviews_rating.all()
        return [
            reverse(
                'provider:review-detail',
                kwargs={'pk': review.pk},
                request=request) for review in reviews
        ]


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

    def get_services_url(self, obj):
        request = self.context.get('request')
        return reverse(
            'provider:service-detail',
            kwargs={'pk': obj.service.pk},
            request=request
        )
