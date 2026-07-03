from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from .models import Advertisement, MapLocation
from .serializers import AdvertisementSerializer, MapLocationSerializer


class AdvertisementViewSet(viewsets.ModelViewSet):
    """Anyone can view ads (even logged-out homepage); admin manages them."""
    queryset = Advertisement.objects.filter(is_active=True)
    serializer_class = AdvertisementSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.ADMIN]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()


class MapLocationViewSet(viewsets.ModelViewSet):
    """Island map points. Public to read; admin maintains them."""
    queryset = MapLocation.objects.all()
    serializer_class = MapLocationSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.ADMIN]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
