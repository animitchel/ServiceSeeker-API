from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


app_name = 'booking_scheduling'

# action = {
#     # 'get': 'list',
#     'post': 'create_request_for_service'
# }

router = DefaultRouter()
router.register(r'service-order',
                views.ServiceOrderViewSet,
                basename='serviceorder'
                )

urlpatterns = [
    path('', include(router.urls))
]
