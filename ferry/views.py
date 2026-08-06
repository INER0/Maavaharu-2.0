from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import viewsets

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from hotels.models import HotelBooking
from .forms import FerryBookingValidationForm, FerryScheduleForm, FerryScheduleSeatForm
from .models import FerrySchedule
from .serializers import FerryScheduleSerializer


def _is_ferry_staff(user):
    return user.is_authenticated and user.role in [User.Role.FERRY_OPERATOR, User.Role.ADMIN]


def ferry_page(request):
    schedules = FerrySchedule.objects.all().order_by('schedule_type', 'date', 'departure_time')

    return render(request, 'ferry/ferry.html', {
        'schedules': schedules,
    })


@login_required(login_url='login')
def ferry_staff_dashboard(request):
    if not _is_ferry_staff(request.user):
        messages.error(request, 'Only ferry operators can access the ferry dashboard.')
        return redirect('home')

    section_choices = {'overview', 'schedules', 'capacity', 'validation', 'passengers', 'reports'}
    active_section = request.GET.get('section', 'overview')
    if active_section not in section_choices:
        active_section = 'overview'

    def staff_section_redirect(section):
        return redirect(f'{request.path}?section={section}')

    schedules = FerrySchedule.objects.all().order_by('schedule_type', 'date', 'departure_time')
    upcoming_schedules = schedules.filter(
        date__gte=timezone.now().date()
    ) | schedules.filter(schedule_type__in=[
        FerrySchedule.ScheduleType.DAILY,
        FerrySchedule.ScheduleType.WEEKLY,
    ])
    eligible_bookings = HotelBooking.objects.filter(
        status=HotelBooking.Status.CONFIRMED,
        check_out__gte=timezone.now().date(),
    ).select_related('visitor', 'room', 'room__hotel').order_by('check_in')

    schedule_form = FerryScheduleForm()
    validation_form = FerryBookingValidationForm()
    validation_result = None
    validation_error = ''
    validation_matches = []

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_schedule':
            active_section = 'schedules'
            schedule_form = FerryScheduleForm(request.POST)
            if schedule_form.is_valid():
                schedule = schedule_form.save(commit=False)
                schedule.price = 0
                schedule.save()
                messages.success(request, 'Ferry schedule added.')
                return staff_section_redirect('schedules')

        elif action == 'update_seats':
            active_section = 'capacity'
            schedule = FerrySchedule.objects.filter(id=request.POST.get('schedule_id')).first()
            if schedule:
                seat_form = FerryScheduleSeatForm(request.POST, instance=schedule)
                if seat_form.is_valid():
                    seat_form.save()
                    messages.success(request, 'Available seats updated.')
                    return staff_section_redirect('capacity')

        elif action == 'delete_schedule':
            active_section = 'schedules'
            schedule = FerrySchedule.objects.filter(id=request.POST.get('schedule_id')).first()
            if schedule:
                schedule.delete()
                messages.success(request, 'Ferry schedule removed.')
                return staff_section_redirect('schedules')

        elif action == 'validate_booking':
            active_section = 'validation'
            validation_form = FerryBookingValidationForm(request.POST)
            if validation_form.is_valid():
                verification_code = validation_form.cleaned_data.get('verification_code')
                username = validation_form.cleaned_data.get('username')
                booking_queryset = HotelBooking.objects.select_related('visitor', 'room', 'room__hotel')

                if username:
                    validation_matches = booking_queryset.filter(
                        Q(visitor__username__icontains=username)
                        | Q(visitor__first_name__icontains=username)
                        | Q(visitor__last_name__icontains=username)
                    ).order_by('-created_at')[:20]
                    if not validation_matches:
                        validation_error = f'No hotel bookings found for visitor "{username}".'
                else:
                    booking = booking_queryset.filter(verification_code=verification_code).first()
                    if booking:
                        validation_result = {
                            'verification_code': booking.verification_code,
                            'guest': booking.visitor.username,
                            'room': booking.room.room_type,
                            'hotel': booking.room.hotel.name,
                            'check_in': booking.check_in,
                            'check_out': booking.check_out,
                            'adults': booking.adults,
                            'kids': booking.kids,
                            'status': booking.get_status_display(),
                            'eligible': booking.is_valid,
                            'message': 'Eligible for ferry transfer.' if booking.is_valid else 'Not eligible for ferry transfer until booking is confirmed and active.',
                        }
                    else:
                        validation_error = 'No hotel booking found with that verification ID.'

    total_capacity = sum(schedule.capacity for schedule in upcoming_schedules)
    total_available_seats = sum(schedule.available_seats for schedule in upcoming_schedules)
    daily_count = schedules.filter(schedule_type=FerrySchedule.ScheduleType.DAILY).count()
    weekly_count = schedules.filter(schedule_type=FerrySchedule.ScheduleType.WEEKLY).count()
    special_count = schedules.filter(schedule_type=FerrySchedule.ScheduleType.SPECIAL).count()

    return render(request, 'ferry/staff_dashboard.html', {
        'schedule_form': schedule_form,
        'validation_form': validation_form,
        'validation_result': validation_result,
        'validation_error': validation_error,
        'validation_matches': validation_matches,
        'schedules': schedules,
        'eligible_bookings': eligible_bookings,
        'upcoming_count': upcoming_schedules.count(),
        'total_capacity': total_capacity,
        'total_available_seats': total_available_seats,
        'eligible_passenger_count': eligible_bookings.count(),
        'daily_count': daily_count,
        'weekly_count': weekly_count,
        'special_count': special_count,
        'active_section': active_section,
    })


class FerryScheduleViewSet(viewsets.ModelViewSet):
    """Anyone logged in can view schedules; only ferry operators/admin edit."""
    queryset = FerrySchedule.objects.all()
    serializer_class = FerryScheduleSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.FERRY_OPERATOR]
