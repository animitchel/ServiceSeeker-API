from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


app_name = 'booking_scheduling'

router = DefaultRouter()
router.register('service-order',
                views.ServiceOrderViewSet,
                basename='service_order'
                )

urlpatterns = [
    path('', include(router.urls))
]
