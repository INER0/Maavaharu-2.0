from rest_framework.routers import DefaultRouter
from .views import AdvertisementViewSet, MapLocationViewSet

router = DefaultRouter()
router.register('advertisements', AdvertisementViewSet)
router.register('map-locations', MapLocationViewSet)

urlpatterns = router.urls
