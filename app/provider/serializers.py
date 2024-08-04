from core.models import ProviderProfile, ServiceType, Review
# from django.contrib.auth import (
#     get_user_model,
# )

# from django.utils.translation import gettext as _

from rest_framework import serializers
from user.serializers import UserSerializer


class ProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

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
            'services',
            'user',
            'created_at', 'updated_at',
        ]

        read_only_fields = [
            'created_at', 'updated_at',
            'user', 'id', 'average_rating',
            'services']
        extra_kwargs = {'user': {'required': True}}


class ServiceTypeSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer(read_only=True)

    class Meta:
        model = ServiceType
        fields = ['id',
                  'service_type', 'description',
                  'pricing', 'availability',
                  'user_reviews_rating',
                  'provider',
                  'created_at', 'updated_at',
                  ]
        read_only_fields = ['id', 'created_at', 'updated_at',
                            'provider', 'user_reviews_rating'
                            ]
        extra_kwargs = {'service_type': {'required': True},
                        'description': {'required': True},
                        'pricing': {'required': True},
                        'availability': {'required': True}
                        }


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    service = ServiceTypeSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'rating',
            'review_text',
            'service', 'user',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at',
                            'updated_at',
                            'service',
                            'user',
                            ]
