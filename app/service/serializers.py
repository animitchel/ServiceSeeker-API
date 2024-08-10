from rest_framework import serializers
from rest_framework.reverse import reverse
from core.models import ServiceType


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

    def get_provider_url(self, obj) -> str:
        request = self.context.get('request')
        return reverse(
            'provider:profile-detail',
            kwargs={'pk': obj.provider.pk},
            request=request
        )

    def get_user_review_rating_url(self, obj) -> list[str]:
        request = self.context.get('request')
        reviews = obj.user_reviews_rating.all()
        return [
            reverse(
                'review:review-detail',
                kwargs={'pk': review.pk},
                request=request) for review in reviews
        ]
