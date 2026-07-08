from django.shortcuts import render
from rest_framework import viewsets

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from .models import FerrySchedule
from .serializers import FerryScheduleSerializer


def ferry_page(request):
    schedules = FerrySchedule.objects.all().order_by('date', 'departure_time')

    return render(request, 'ferry/ferry.html', {
        'schedules': schedules,
    })


class FerryScheduleViewSet(viewsets.ModelViewSet):
    """Anyone logged in can view schedules; only ferry operators/admin edit."""
    queryset = FerrySchedule.objects.all()
    serializer_class = FerryScheduleSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.FERRY_OPERATOR]
