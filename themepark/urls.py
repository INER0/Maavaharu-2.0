from rest_framework.routers import DefaultRouter
from .views import (
    EventViewSet, ThemeParkEntranceTicketViewSet,
    ThemeParkPromotionViewSet, ThemeParkTicketViewSet,
)

router = DefaultRouter()
router.register('events', EventViewSet)
router.register('themepark-tickets', ThemeParkTicketViewSet, basename='themepark-tickets')
router.register('themepark-entrance-tickets', ThemeParkEntranceTicketViewSet, basename='themepark-entrance-tickets')
router.register('themepark-promotions', ThemeParkPromotionViewSet)

urlpatterns = router.urls
