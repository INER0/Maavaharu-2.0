from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, RoomViewSet, HotelBookingViewSet, HotelPromotionViewSet

router = DefaultRouter()
router.register('hotels', HotelViewSet)
router.register('rooms', RoomViewSet)
router.register('hotel-bookings', HotelBookingViewSet, basename='hotel-bookings')
router.register('hotel-promotions', HotelPromotionViewSet)

urlpatterns = router.urls
