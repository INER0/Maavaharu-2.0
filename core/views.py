from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from hotels.models import Hotel, HotelPromotion
from themepark.models import Event
from .models import Advertisement, MapLocation
from .serializers import AdvertisementSerializer, MapLocationSerializer


def home(request):
    advertisements = Advertisement.objects.filter(is_active=True).order_by('-created_at')[:3]
    promotions = HotelPromotion.objects.prefetch_related('images').all().order_by('valid_until')[:3]
    hotels = Hotel.objects.prefetch_related('rooms__images').all()[:3]
    events = Event.objects.all().order_by('date', 'time')[:4]
    locations = MapLocation.objects.all()[:5]

    return render(request, 'home.html', {
        'advertisements': advertisements,
        'promotions': promotions,
        'hotels': hotels,
        'events': events,
        'locations': locations,
    })


def island_map_page(request):
    locations = MapLocation.objects.all().order_by('category', 'name')

    return render(request, 'core/map.html', {
        'locations': locations,
    })


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
