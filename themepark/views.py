from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from .models import Event, ThemeParkTicket
from .serializers import EventSerializer, ThemeParkTicketSerializer


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
