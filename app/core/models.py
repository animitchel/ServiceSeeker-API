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
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone


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
    last_login = models.DateTimeField(auto_now=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ['-date_joined']


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
    # bio = models.TextField(blank=True, null=True)
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

    location = models.CharField(
        choices=lists_of_choices.LOCATION,
        max_length=255, blank=True, null=True
    )

    profile_picture = models.ImageField(
        upload_to=service_seeker_image_file_path, blank=True, null=True,
    )

    bio = models.TextField(blank=True, null=True, max_length=400)

    experience_years = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        help_text="Experience_years must be between 1 and 99.",
        blank=True, null=True, default=0,
    )

    certifications = models.TextField(blank=True, null=True, max_length=255)

    # is_verified = models.BooleanField(default=False)
    certifications_documents = models.FileField(
        upload_to=service_seeker_image_file_path,
        blank=True, null=True
    )
    # pricing_details = models.TextField(blank=True, null=True)

    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2,
        blank=True, null=True
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

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
        return (f""
                f"{self.user.first_name} {self.user.last_name}: "
                f"{self.location}"
                )

    class Meta:
        ordering = ['-created_at']


class ServiceType(models.Model):
    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE,
        related_name='services',
        null=True,
    )

    service_type = models.CharField(
        choices=lists_of_choices.SERVICE_TYPES,
        max_length=50, unique=True,
        blank=True
    )
    description = models.TextField(max_length=255, null=True)
    pricing = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('0.00'), null=True,
        blank=True
    )

    availability = models.CharField(
        choices=lists_of_choices.AVAILABILITY,
        max_length=255, blank=True, null=True
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (f''
                f'{self.provider.user.first_name}: '
                f'{self.service_type}, {self.pricing}'
                )

    class Meta:
        ordering = ['-created_at']


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_rating'
    )
    service = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE,
        related_name='user_reviews_rating',
        null=True
    )

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating must be between 1 and 5.",
        null=True, blank=True
    )
    review_text = models.TextField(
        max_length=500, blank=True, null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (f"Rating: "
                f"{self.user.first_name}: {self.rating}, "
                f"Review: {self.review_text}"
                )

    class Meta:
        ordering = ['-created_at']


class ServiceOrder(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='service_orders'
    )
    service = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE,
        related_name='service_orders'
    )
    order_date = models.DateTimeField(auto_now_add=True)

    appointment_date = models.DateTimeField(null=True)
    is_appointment = models.BooleanField(default=False)

    status = models.CharField(
        max_length=50, choices=lists_of_choices.PROCESS_STATE,
        default='pending')
    details = models.TextField(
        blank=True, null=True, max_length=500
    )

    def __str__(self):
        return (f''
                f'{self.user.first_name} - '
                f'{self.service.service_type} ordered on '
                f'{self.order_date}'
                )

    class Meta:
        verbose_name_plural = 'ServiceOrder'
        ordering = ['-order_date']
