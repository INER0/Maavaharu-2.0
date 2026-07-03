from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from .models import FerrySchedule, FerryTicket
from .serializers import FerryScheduleSerializer, FerryTicketSerializer


class FerryScheduleViewSet(viewsets.ModelViewSet):
    """Anyone logged in can view schedules; only ferry operators/admin edit."""
    queryset = FerrySchedule.objects.all()
    serializer_class = FerryScheduleSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.FERRY_OPERATOR]


class FerryTicketViewSet(viewsets.ModelViewSet):
    serializer_class = FerryTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.FERRY_OPERATOR, User.Role.ADMIN]:
            return FerryTicket.objects.all().order_by('-issued_at')
        return FerryTicket.objects.filter(visitor=user).order_by('-issued_at')

    def perform_create(self, serializer):
        # Save the ticket, reduce the seats left, mark it issued.
        ticket = serializer.save(visitor=self.request.user)
        schedule = ticket.schedule
        schedule.available_seats -= ticket.seats
        schedule.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def issue(self, request, pk=None):
        """Ferry operator endpoint: POST /api/ferry-tickets/<id>/issue/
        to mark a pending ticket as officially issued."""
        ticket = self.get_object()
        if request.user.role not in [User.Role.FERRY_OPERATOR, User.Role.ADMIN]:
            return Response({'detail': 'Only ferry operators can issue passes.'}, status=403)
        ticket.status = FerryTicket.Status.ISSUED
        ticket.save()
        return Response(FerryTicketSerializer(ticket, context={'request': request}).data)
