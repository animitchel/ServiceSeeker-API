from django.urls import path, include

from rest_framework.routers import DefaultRouter
from review import views

app_name = 'review'

router = DefaultRouter()
router.register('service-review', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
