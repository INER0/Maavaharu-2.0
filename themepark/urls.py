from rest_framework.routers import DefaultRouter
from .views import EventViewSet, ThemeParkTicketViewSet

router = DefaultRouter()
router.register('events', EventViewSet)
router.register('themepark-tickets', ThemeParkTicketViewSet, basename='themepark-tickets')

urlpatterns = router.urls
