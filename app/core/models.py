"""
Database models.
"""
from django.conf import settings
from . import lists_of_choices
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import uuid
import os


def service_seeker_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'service_seeker', filename)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class ServiceType(models.Model):
    name = models.CharField(
        choices=lists_of_choices.SERVICE_TYPES,
        max_length=50, unique=True
    )

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_profile'
    )

    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(
        choices=lists_of_choices.TOP_CITIES,
        max_length=255, blank=True, null=True
    )
    state = models.CharField(
        choices=lists_of_choices.TOP_STATES_PROVINCES,
        max_length=255, blank=True, null=True)

    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(
        choices=lists_of_choices.SUPPORTED_COUNTRIES,
        max_length=255, blank=True, null=True
    )
    profile_picture = models.ImageField(
        upload_to=service_seeker_image_file_path,
        blank=True, null=True
    )
    bio = models.TextField(blank=True, null=True)
    availability = models.CharField(
        choices=lists_of_choices.STATUS_CHOICES,
        max_length=255, blank=True, null=True
    )
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(r'^\+?1?\d{9,15}$',
                           message="Phone number must be "
                                   "entered in the format: "
                                   "'+999999999'. Up to 15 "
                                   "digits allowed."
                           )
        ])

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class ProviderProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='provider_profile'
    )
    service_types = models.ManyToManyField(
        ServiceType,
        related_name='provider_service_types'
    )

    city = models.CharField(
        choices=lists_of_choices.TOP_CITIES,
        max_length=255, blank=True, null=True
    )
    state = models.CharField(
        choices=lists_of_choices.TOP_STATES_PROVINCES,
        max_length=255, blank=True, null=True
    )
    country = models.CharField(
        choices=lists_of_choices.SUPPORTED_COUNTRIES,
        max_length=255, blank=True, null=True
    )
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='images/', blank=True, null=True
    )
    bio = models.TextField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    availability = models.CharField(
        choices=lists_of_choices.STATUS_CHOICES,
        max_length=255, blank=True, null=True
    )
    is_verified = models.BooleanField(default=False)
    documents = models.FileField(
        upload_to='provider_documents/',
        blank=True, null=True
    )
    pricing_details = models.TextField(blank=True, null=True)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2,
        blank=True, null=True
    )
    phone_number = models.CharField(
        max_length=15,
        null=True,
        validators=[
            RegexValidator(r'^\+?1?\d{9,15}$',
                           message="Phone number must be "
                                   "entered in the format: "
                                   "'+999999999'. Up to 15 "
                                   "digits allowed."
                           )
        ])

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
