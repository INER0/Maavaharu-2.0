from django.contrib import messages
from django.shortcuts import redirect, render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from .forms import ThemeParkTicketForm
from .models import Event, ThemeParkTicket
from .serializers import EventSerializer, ThemeParkTicketSerializer


def themepark_page(request):
    activities = Event.objects.exclude(
        event_type=Event.EventType.BEACH
    ).order_by('date', 'time')
    beach_events = Event.objects.filter(
        event_type=Event.EventType.BEACH
    ).order_by('date', 'time')
    upcoming_dates = Event.objects.order_by('date').values_list('date', flat=True).distinct()
    user_tickets = []

    if request.user.is_authenticated:
        user_tickets = ThemeParkTicket.objects.filter(visitor=request.user).select_related(
            'event'
        ).order_by('-purchased_at')[:5]

    activity_form = ThemeParkTicketForm(event_type=None, prefix='activity')
    beach_form = ThemeParkTicketForm(event_type=Event.EventType.BEACH, prefix='beach')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please login before purchasing tickets.')
            return redirect('login')

        form_kind = request.POST.get('form_kind')
        if form_kind == 'beach':
            beach_form = ThemeParkTicketForm(request.POST, event_type=Event.EventType.BEACH, prefix='beach')
            form = beach_form
        else:
            activity_form = ThemeParkTicketForm(request.POST, event_type=None, prefix='activity')
            form = activity_form

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.visitor = request.user
            ticket.channel = ThemeParkTicket.Channel.ONLINE
            ticket.save()

            event = ticket.event
            event.available_capacity -= ticket.quantity
            event.save()

            messages.success(request, 'Your theme park ticket purchase has been recorded.')
            return redirect('themepark')

    return render(request, 'themepark/themepark.html', {
        'activities': activities,
        'beach_events': beach_events,
        'upcoming_dates': upcoming_dates,
        'activity_form': activity_form,
        'beach_form': beach_form,
        'user_tickets': user_tickets,
    })


class EventViewSet(viewsets.ModelViewSet):
    """Visitors browse events; theme park staff/admin create and manage them."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.THEMEPARK_STAFF]


class ThemeParkTicketViewSet(viewsets.ModelViewSet):
    serializer_class = ThemeParkTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.THEMEPARK_STAFF, User.Role.ADMIN]:
            return ThemeParkTicket.objects.all().order_by('-purchased_at')
        return ThemeParkTicket.objects.filter(visitor=user).order_by('-purchased_at')

    def perform_create(self, serializer):
        ticket = serializer.save(visitor=self.request.user)
        event = ticket.event
        event.available_capacity -= ticket.quantity
        event.save()
