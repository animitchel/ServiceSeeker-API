"""
Serializer for the user API view.
"""
from django.contrib.auth import (
    get_user_model,
)

# from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password', 'first_name',
                  'last_name', 'user_profile', 'provider_profile',
                  'date_joined',
                  ]
        extra_kwargs = {
            'password': {
                'write_only': True, 'min_length': 5,
                'required': True
            },
            'first_name': {'required': True},
            'email': {'required': True},
        }
        read_only_fields = ['user_profile', 'provider_profile']

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        user = get_user_model().objects.create_user(**validated_data)

        # user profile created automatically for new user
        # a user can also be a provider and vise versa
        # UserProfile.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        """Update and return user object"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
