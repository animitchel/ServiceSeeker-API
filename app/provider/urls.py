"""
URL Mappings for the Provider app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from provider import views

app_name = 'provider'

router = DefaultRouter()
router.register('profile', views.ProviderViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
