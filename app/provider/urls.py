"""
URL Mappings for the Provider app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from provider import views

router = DefaultRouter()
router.register('provider', views.ProviderViewSet)
router.register('service', views.ServiceTypeViewSet)
router.register('review', views.ReviewViewSet)

app_name = 'provider'

urlpatterns = [
    path('', include(router.urls)),
]
