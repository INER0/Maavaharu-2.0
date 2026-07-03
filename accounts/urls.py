from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, MeView, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/me/', MeView.as_view(), name='me'),
]
urlpatterns += router.urls
