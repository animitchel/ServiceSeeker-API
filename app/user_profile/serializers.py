from core.models import UserProfile

# from django.utils.translation import gettext as _

from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for the User profile object."""

    class Meta:
        model = UserProfile
        fields = [
            'id', 'address', 'city', 'state',
            'country', 'postal_code',
            'availability', 'email_notifications',
            'sms_notifications', 'phone_number',
            'profile_picture', 'user',
        ]
        read_only_fields = ['id', 'user']
        extra_kwargs = {'user': {'required': True}}

    def update(self, instance, validated_data):
        profile_picture_data = validated_data.pop('profile_picture', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if profile_picture_data:
            instance.profile_picture = profile_picture_data

        instance.save()
        return instance
