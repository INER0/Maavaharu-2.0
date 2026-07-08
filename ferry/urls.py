from rest_framework.routers import DefaultRouter
from .views import FerryScheduleViewSet

router = DefaultRouter()
router.register('ferry-schedules', FerryScheduleViewSet)

urlpatterns = router.urls
