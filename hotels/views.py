from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from datetime import date
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from .forms import (
    HotelBookingForm, HotelBookingStatusForm, HotelStaffHotelForm,
    HotelStaffPromotionForm, HotelStaffRoomForm,
)
from .models import Hotel, Room, HotelBooking, HotelPromotion, HotelPromotionImage, RoomImage
from .serializers import (
    HotelSerializer, RoomSerializer, HotelBookingSerializer, HotelPromotionSerializer,
)


def _is_hotel_staff(user):
    return user.is_authenticated and user.role in [User.Role.HOTEL_MANAGER, User.Role.ADMIN]


@login_required(login_url='login')
def room_availability(request):
    room_id = request.GET.get('room')
    check_in_value = request.GET.get('check_in')
    check_out_value = request.GET.get('check_out')
    requested_rooms = request.GET.get('num_rooms') or 1

    try:
        check_in = date.fromisoformat(check_in_value)
        check_out = date.fromisoformat(check_out_value)
        requested_rooms = int(requested_rooms)
    except (TypeError, ValueError):
        return JsonResponse({
            'available': False,
            'message': 'Choose a valid room, check-in date, and check-out date.',
        }, status=400)

    room = Room.objects.filter(id=room_id).first()
    if not room:
        return JsonResponse({
            'available': False,
            'message': 'Choose a valid room type.',
        }, status=404)

    if check_in < date.today():
        return JsonResponse({
            'available': False,
            'message': 'Check-in date cannot be in the past.',
        }, status=400)

    if check_out <= check_in:
        return JsonResponse({
            'available': False,
            'message': 'Check-out date must be after check-in date.',
        }, status=400)

    occupied_rooms = room.occupied_rooms(check_in, check_out)
    available_rooms = room.available_rooms(check_in, check_out)
    has_enough_rooms = requested_rooms <= available_rooms

    if has_enough_rooms:
        message = f'{available_rooms} room(s) available for these dates.'
    else:
        message = f'Only {available_rooms} room(s) available after pending and confirmed bookings. Choose fewer rooms or different dates.'

    return JsonResponse({
        'available': has_enough_rooms,
        'total_rooms': room.total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'requested_rooms': requested_rooms,
        'message': message,
    })


@login_required(login_url='login')
def hotel_booking_page(request):
    hotel = Hotel.objects.prefetch_related('rooms__images').first()
    rooms = Room.objects.select_related('hotel').prefetch_related('images').all()
    promotions = HotelPromotion.objects.select_related('hotel').prefetch_related('images').order_by('valid_until')[:3]
    user_bookings = HotelBooking.objects.filter(visitor=request.user).select_related(
        'room', 'room__hotel'
    ).order_by('-created_at')[:5]

    selected_room = None

    if request.method == 'POST':
        form = HotelBookingForm(request.POST)
        selected_room = Room.objects.filter(id=request.POST.get('room')).first()
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
        'selected_room': selected_room,
    })


@login_required(login_url='login')
def hotel_staff_dashboard(request):
    if not _is_hotel_staff(request.user):
        messages.error(request, 'Only hotel staff can access the Maavaharu Hotel dashboard.')
        return redirect('home')

    hotel = Hotel.objects.first()
    rooms = Room.objects.select_related('hotel').prefetch_related('images').order_by('room_type')
    bookings = HotelBooking.objects.select_related('visitor', 'room', 'room__hotel').order_by('-created_at')
    promotions = HotelPromotion.objects.select_related('hotel').prefetch_related('images').order_by('valid_until')

    hotel_form = HotelStaffHotelForm(instance=hotel)
    room_form = HotelStaffRoomForm()
    promotion_form = HotelStaffPromotionForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_hotel':
            hotel_form = HotelStaffHotelForm(request.POST, instance=hotel)
            if hotel_form.is_valid():
                hotel_form.save()
                messages.success(request, 'Maavaharu Hotel details saved.')
                return redirect('hotel_staff')

        elif action == 'add_room':
            room_form = HotelStaffRoomForm(request.POST, request.FILES)
            if room_form.is_valid():
                room = room_form.save()
                for image in request.FILES.getlist('images'):
                    RoomImage.objects.create(room=room, image=image)
                messages.success(request, 'Room availability added.')
                return redirect('hotel_staff')

        elif action == 'add_promotion':
            promotion_form = HotelStaffPromotionForm(request.POST, request.FILES)
            if promotion_form.is_valid():
                promotion = promotion_form.save()
                for image in request.FILES.getlist('images'):
                    HotelPromotionImage.objects.create(promotion=promotion, image=image)
                messages.success(request, 'Hotel promotion added.')
                return redirect('hotel_staff')

        elif action == 'update_booking':
            booking_id = request.POST.get('booking_id')
            booking = HotelBooking.objects.filter(id=booking_id).first()
            if booking:
                status_form = HotelBookingStatusForm(request.POST, instance=booking)
                if status_form.is_valid():
                    status_form.save()
                    messages.success(request, 'Booking status updated.')
                    return redirect('hotel_staff')

    pending_count = bookings.filter(status=HotelBooking.Status.PENDING).count()
    confirmed_count = bookings.filter(status=HotelBooking.Status.CONFIRMED).count()
    cancelled_count = bookings.filter(status=HotelBooking.Status.CANCELLED).count()
    total_rooms = sum(room.total_rooms for room in rooms)

    return render(request, 'hotels/staff_dashboard.html', {
        'hotel': hotel,
        'rooms': rooms,
        'bookings': bookings,
        'promotions': promotions,
        'hotel_form': hotel_form,
        'room_form': room_form,
        'promotion_form': promotion_form,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'cancelled_count': cancelled_count,
        'total_rooms': total_rooms,
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
