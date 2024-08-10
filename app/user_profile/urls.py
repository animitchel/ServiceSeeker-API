from django.urls import path
from user_profile import views


app_name = 'user_profile'

urlpatterns = [
    path(
        'profile/',
        views.ManageUserProfileView.as_view(),
        name='manage_user_profile'
    )
]
