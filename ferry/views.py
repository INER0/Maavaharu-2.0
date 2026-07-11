from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import viewsets

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from hotels.models import HotelBooking
from .forms import FerryScheduleForm, FerryScheduleSeatForm
from .models import FerrySchedule
from .serializers import FerryScheduleSerializer


def _is_ferry_staff(user):
    return user.is_authenticated and user.role in [User.Role.FERRY_OPERATOR, User.Role.ADMIN]


def ferry_page(request):
    schedules = FerrySchedule.objects.all().order_by('date', 'departure_time')

    return render(request, 'ferry/ferry.html', {
        'schedules': schedules,
    })


@login_required(login_url='login')
def ferry_staff_dashboard(request):
    if not _is_ferry_staff(request.user):
        messages.error(request, 'Only ferry operators can access the ferry dashboard.')
        return redirect('home')

    schedules = FerrySchedule.objects.all().order_by('date', 'departure_time')
    upcoming_schedules = schedules.filter(date__gte=timezone.now().date())
    eligible_bookings = HotelBooking.objects.filter(
        status=HotelBooking.Status.CONFIRMED,
        check_out__gte=timezone.now().date(),
    ).select_related('visitor', 'room', 'room__hotel').order_by('check_in')

    schedule_form = FerryScheduleForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_schedule':
            schedule_form = FerryScheduleForm(request.POST)
            if schedule_form.is_valid():
                schedule = schedule_form.save(commit=False)
                schedule.price = 0
                schedule.save()
                messages.success(request, 'Ferry schedule added.')
                return redirect('ferry_staff')

        elif action == 'update_seats':
            schedule = FerrySchedule.objects.filter(id=request.POST.get('schedule_id')).first()
            if schedule:
                seat_form = FerryScheduleSeatForm(request.POST, instance=schedule)
                if seat_form.is_valid():
                    seat_form.save()
                    messages.success(request, 'Available seats updated.')
                    return redirect('ferry_staff')

        elif action == 'delete_schedule':
            schedule = FerrySchedule.objects.filter(id=request.POST.get('schedule_id')).first()
            if schedule:
                schedule.delete()
                messages.success(request, 'Ferry schedule removed.')
                return redirect('ferry_staff')

    total_capacity = sum(schedule.capacity for schedule in upcoming_schedules)
    total_available_seats = sum(schedule.available_seats for schedule in upcoming_schedules)

    return render(request, 'ferry/staff_dashboard.html', {
        'schedule_form': schedule_form,
        'schedules': schedules,
        'eligible_bookings': eligible_bookings,
        'upcoming_count': upcoming_schedules.count(),
        'total_capacity': total_capacity,
        'total_available_seats': total_available_seats,
        'eligible_passenger_count': eligible_bookings.count(),
    })


class FerryScheduleViewSet(viewsets.ModelViewSet):
    """Anyone logged in can view schedules; only ferry operators/admin edit."""
    queryset = FerrySchedule.objects.all()
    serializer_class = FerryScheduleSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.FERRY_OPERATOR]
