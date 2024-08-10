from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from service import views

app_name = 'service'

router = DefaultRouter()
router.register('service-type', views.ServiceTypeViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
]
