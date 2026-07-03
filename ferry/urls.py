from rest_framework.routers import DefaultRouter
from .views import FerryScheduleViewSet, FerryTicketViewSet

router = DefaultRouter()
router.register('ferry-schedules', FerryScheduleViewSet)
router.register('ferry-tickets', FerryTicketViewSet, basename='ferry-tickets')

urlpatterns = router.urls
