from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from .forms import HotelBookingForm
from .models import Hotel, Room, HotelBooking, HotelPromotion
from .serializers import (
    HotelSerializer, RoomSerializer, HotelBookingSerializer, HotelPromotionSerializer,
)


@login_required(login_url='login')
def hotel_booking_page(request):
    hotel = Hotel.objects.prefetch_related('rooms').first()
    rooms = Room.objects.select_related('hotel').all()
    promotions = HotelPromotion.objects.select_related('hotel').order_by('valid_until')[:3]
    user_bookings = HotelBooking.objects.filter(visitor=request.user).select_related(
        'room', 'room__hotel'
    ).order_by('-created_at')[:5]

    if request.method == 'POST':
        form = HotelBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.visitor = request.user
            booking.save()
            messages.success(request, 'Your Maavaharu room booking request has been created.')
            return redirect('hotel_booking')
    else:
        form = HotelBookingForm()

    return render(request, 'hotels/booking.html', {
        'form': form,
        'hotel': hotel,
        'rooms': rooms,
        'promotions': promotions,
        'user_bookings': user_bookings,
    })


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
