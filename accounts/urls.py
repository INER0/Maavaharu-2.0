from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, MeView, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/login/', LoginView.as_view(), name='api_login'),
    path('auth/me/', MeView.as_view(), name='api_me'),
]
urlpatterns += router.urls
