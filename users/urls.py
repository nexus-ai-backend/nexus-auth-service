from django.urls import path

from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("login/",LoginView.as_view(), name="user-login"),
    path("me/", CurrentUserView.as_view(), name="user-me"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]