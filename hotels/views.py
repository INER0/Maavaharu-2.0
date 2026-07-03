from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from .models import Hotel, Room, HotelBooking, HotelPromotion
from .serializers import (
    HotelSerializer, RoomSerializer, HotelBookingSerializer, HotelPromotionSerializer,
)


class HotelViewSet(viewsets.ModelViewSet):
    """Browse hotels (anyone logged in); only hotel managers/admin can edit."""
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.HOTEL_MANAGER]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.HOTEL_MANAGER]


class HotelBookingViewSet(viewsets.ModelViewSet):
    """Visitors create/see their own bookings; managers/admin see all."""
    serializer_class = HotelBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.HOTEL_MANAGER, User.Role.ADMIN]:
            return HotelBooking.objects.all().order_by('-created_at')
        return HotelBooking.objects.filter(visitor=user).order_by('-created_at')

    def perform_create(self, serializer):
        # Attach the booking to whoever is logged in.
        serializer.save(visitor=self.request.user)


class HotelPromotionViewSet(viewsets.ModelViewSet):
    queryset = HotelPromotion.objects.all()
    serializer_class = HotelPromotionSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.HOTEL_MANAGER]
