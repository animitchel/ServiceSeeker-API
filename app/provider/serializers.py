from core.models import ProviderProfile, ServiceType, Review
# from django.contrib.auth import (
#     get_user_model,
# )

# from django.utils.translation import gettext as _

from rest_framework import serializers


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderProfile
        # exclude = ('average_rating',)
        fields = [
            'id',
            'user',
            'location',
            'profile_picture',
            'bio',
            'experience_years',
            'certifications',
            'certifications_documents',
            'average_rating',
            'created_at',
            'updated_at',
            'phone_number',
            'services',
        ]

        read_only_fields = [
            'created_at', 'updated_at',
            'user', 'id', 'average_rating',
            'services']
        extra_kwargs = {'user': {'required': True}}


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'provider',
                  'service_type', 'description',
                  'pricing', 'availability',
                  'created_at', 'updated_at',
                  'user_reviews_rating',
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
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['id', 'created_at',
                            'updated_at', 'user',
                            'service'
                            ]
        required = '__all__'

    # def create(self, validated_data):
    #     auth_user = self.context['request'].user
