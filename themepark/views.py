from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from core.cart import add_entrance_ticket, add_themepark_ticket
from .forms import (
    ActivityTicketSaleForm, EntranceTicketSaleForm, EventCapacityForm, SpecialEventStaffForm,
    ThemeParkEntranceTicketForm, ThemeParkPromotionForm, ThemeParkTicketForm,
    TicketValidationForm,
    WeeklyEventStaffForm,
)
from .models import (
    Event, EventImage, SpecialThemeParkEvent, ThemeParkEntranceTicket, ThemeParkPromotion,
    ThemeParkTicket, WeeklyThemeParkEvent,
)
from .serializers import (
    EventSerializer, ThemeParkEntranceTicketSerializer,
    ThemeParkPromotionSerializer, ThemeParkTicketSerializer,
)


def _is_themepark_staff(user):
    return user.is_authenticated and user.role in [User.Role.THEMEPARK_STAFF, User.Role.ADMIN]


ENTRANCE_TICKET_PRICE = 100


def themepark_page(request):
    activities = Event.objects.exclude(
        event_type=Event.EventType.BEACH
    ).prefetch_related('images').order_by('schedule_type', 'weekday', 'date', 'time')
    weekly_activities = activities.filter(schedule_type=Event.ScheduleType.WEEKLY)
    special_events = activities.filter(schedule_type=Event.ScheduleType.SPECIAL)
    beach_events = Event.objects.filter(
        event_type=Event.EventType.BEACH
    ).prefetch_related('images').order_by('schedule_type', 'weekday', 'date', 'time')
    special_dates = Event.objects.filter(
        schedule_type=Event.ScheduleType.SPECIAL,
        date__isnull=False,
    ).order_by('date').values_list('date', flat=True).distinct()
    weekly_schedules = Event.objects.filter(
        schedule_type=Event.ScheduleType.WEEKLY,
    ).prefetch_related('images').order_by('weekday', 'time')
    promotions = ThemeParkPromotion.objects.select_related('event').order_by('valid_until')[:4]
    user_tickets = []
    user_entrance_tickets = []

    if request.user.is_authenticated:
        user_tickets = ThemeParkTicket.objects.filter(visitor=request.user).select_related(
            'event'
        ).order_by('-purchased_at')[:5]
        user_entrance_tickets = ThemeParkEntranceTicket.objects.filter(
            visitor=request.user
        ).order_by('-purchased_at')[:5]

    entrance_form = ThemeParkEntranceTicketForm(prefix='entrance')
    activity_form = ThemeParkTicketForm(
        exclude_event_type=Event.EventType.BEACH,
        prefix='activity',
    )
    beach_form = ThemeParkTicketForm(event_type=Event.EventType.BEACH, prefix='beach')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please login before purchasing tickets.')
            return redirect('login')

        form_kind = request.POST.get('form_kind')
        if form_kind == 'entrance':
            entrance_form = ThemeParkEntranceTicketForm(request.POST, prefix='entrance')
            form = entrance_form
        elif form_kind == 'beach':
            beach_form = ThemeParkTicketForm(request.POST, event_type=Event.EventType.BEACH, prefix='beach')
            form = beach_form
        else:
            activity_form = ThemeParkTicketForm(
                request.POST,
                exclude_event_type=Event.EventType.BEACH,
                prefix='activity',
            )
            form = activity_form

        if form.is_valid():
            if form_kind == 'entrance':
                add_entrance_ticket(request, form.cleaned_data)
                messages.success(request, 'Entrance ticket added to your cart. Review and pay to complete checkout.')
                return redirect('cart')

            add_themepark_ticket(request, form.cleaned_data)
            messages.success(request, 'Theme park ticket added to your cart. Review and pay to complete checkout.')
            return redirect('cart')

    return render(request, 'themepark/themepark.html', {
        'activities': activities,
        'weekly_activities': weekly_activities,
        'special_events': special_events,
        'beach_events': beach_events,
        'special_dates': special_dates,
        'weekly_schedules': weekly_schedules,
        'promotions': promotions,
        'entrance_form': entrance_form,
        'entrance_ticket_price': ENTRANCE_TICKET_PRICE,
        'activity_form': activity_form,
        'beach_form': beach_form,
        'user_tickets': user_tickets,
        'user_entrance_tickets': user_entrance_tickets,
    })


@login_required(login_url='login')
def themepark_staff_dashboard(request):
    if not _is_themepark_staff(request.user):
        messages.error(request, 'Only theme park staff can access the theme park dashboard.')
        return redirect('home')

    section_choices = {
        'overview', 'schedule', 'capacity', 'bookings',
        'tickets', 'validation', 'promotions', 'reports',
    }
    active_section = request.GET.get('section', 'overview')
    if active_section not in section_choices:
        active_section = 'overview'

    def staff_section_redirect(section):
        return redirect(f'{request.path}?section={section}')

    weekly_events = WeeklyThemeParkEvent.objects.prefetch_related('tickets', 'images').order_by('weekday', 'time')
    special_events = SpecialThemeParkEvent.objects.prefetch_related('tickets', 'images').order_by('date', 'time')
    events = list(Event.objects.prefetch_related('tickets', 'images').annotate(
        booked_total=Coalesce(Sum('tickets__quantity'), 0),
        online_booked=Coalesce(
            Sum('tickets__quantity', filter=Q(tickets__channel=ThemeParkTicket.Channel.ONLINE)),
            0,
        ),
        entrance_booked=Coalesce(
            Sum('tickets__quantity', filter=Q(tickets__channel=ThemeParkTicket.Channel.ENTRANCE)),
            0,
        ),
        visitor_count=Count('tickets__visitor', distinct=True),
    ).order_by('schedule_type', 'weekday', 'date', 'time'))
    tickets = ThemeParkTicket.objects.select_related('visitor', 'event').order_by('-purchased_at')
    entrance_tickets = ThemeParkEntranceTicket.objects.select_related('visitor').order_by('-purchased_at')
    promotions = ThemeParkPromotion.objects.select_related('event').order_by('valid_until')

    weekly_event_form = WeeklyEventStaffForm()
    special_event_form = SpecialEventStaffForm()
    activity_ticket_form = ActivityTicketSaleForm()
    entrance_ticket_form = EntranceTicketSaleForm()
    promotion_form = ThemeParkPromotionForm()
    validation_form = TicketValidationForm()
    validation_result = None
    validation_error = ''

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_weekly_event':
            active_section = 'schedule'
            weekly_event_form = WeeklyEventStaffForm(request.POST, request.FILES)
            if weekly_event_form.is_valid():
                event = weekly_event_form.save()
                for image in request.FILES.getlist('images'):
                    EventImage.objects.create(event=event, image=image)
                messages.success(request, 'Weekly theme park activity added.')
                return staff_section_redirect('schedule')

        elif action == 'add_special_event':
            active_section = 'schedule'
            special_event_form = SpecialEventStaffForm(request.POST, request.FILES)
            if special_event_form.is_valid():
                event = special_event_form.save()
                for image in request.FILES.getlist('images'):
                    EventImage.objects.create(event=event, image=image)
                messages.success(request, 'Special theme park event added.')
                return staff_section_redirect('schedule')

        elif action == 'update_capacity':
            active_section = 'capacity'
            event = Event.objects.filter(id=request.POST.get('event_id')).first()
            if event:
                capacity_form = EventCapacityForm(request.POST, instance=event)
                if capacity_form.is_valid():
                    capacity_form.save()
                    messages.success(request, 'Event availability updated.')
                    return staff_section_redirect('capacity')

        elif action == 'delete_event':
            active_section = 'schedule'
            event = Event.objects.filter(id=request.POST.get('event_id')).first()
            if event:
                event.delete()
                messages.success(request, 'Theme park event removed.')
                return staff_section_redirect('schedule')

        elif action == 'sell_activity_ticket':
            active_section = 'tickets'
            activity_ticket_form = ActivityTicketSaleForm(request.POST)
            if activity_ticket_form.is_valid():
                ticket = activity_ticket_form.save(commit=False)
                ticket.channel = ThemeParkTicket.Channel.ENTRANCE
                ticket.save()
                event = ticket.event
                if event.available_capacity is not None:
                    event.available_capacity -= ticket.quantity
                    event.save()
                messages.success(request, 'Activity ticket sale recorded.')
                return staff_section_redirect('tickets')

        elif action == 'sell_entrance_ticket':
            active_section = 'tickets'
            entrance_ticket_form = EntranceTicketSaleForm(request.POST)
            if entrance_ticket_form.is_valid():
                entrance_ticket = entrance_ticket_form.save(commit=False)
                entrance_ticket.channel = ThemeParkEntranceTicket.Channel.ENTRANCE
                entrance_ticket.price_per_ticket = ENTRANCE_TICKET_PRICE
                entrance_ticket.save()
                messages.success(request, 'Theme park entrance ticket sale recorded.')
                return staff_section_redirect('tickets')

        elif action == 'delete_ticket':
            active_section = 'tickets'
            ticket = ThemeParkTicket.objects.select_related('event').filter(id=request.POST.get('ticket_id')).first()
            if ticket:
                event = ticket.event
                if event.capacity is not None and event.available_capacity is not None:
                    event.available_capacity = min(event.capacity, event.available_capacity + ticket.quantity)
                    event.save()
                ticket.delete()
                messages.success(request, 'Ticket record removed and capacity restored.')
                return staff_section_redirect('tickets')

        elif action == 'delete_entrance_ticket':
            active_section = 'tickets'
            entrance_ticket = ThemeParkEntranceTicket.objects.filter(id=request.POST.get('entrance_ticket_id')).first()
            if entrance_ticket:
                entrance_ticket.delete()
                messages.success(request, 'Entrance ticket record removed.')
                return staff_section_redirect('tickets')

        elif action == 'add_promotion':
            active_section = 'promotions'
            promotion_form = ThemeParkPromotionForm(request.POST)
            if promotion_form.is_valid():
                promotion_form.save()
                messages.success(request, 'Activity promotion added.')
                return staff_section_redirect('promotions')

        elif action == 'delete_promotion':
            active_section = 'promotions'
            promotion = ThemeParkPromotion.objects.filter(id=request.POST.get('promotion_id')).first()
            if promotion:
                promotion.delete()
                messages.success(request, 'Activity promotion removed.')
                return staff_section_redirect('promotions')

        elif action == 'validate_ticket':
            active_section = 'validation'
            validation_form = TicketValidationForm(request.POST)
            if validation_form.is_valid():
                ticket_type = validation_form.cleaned_data['ticket_type']
                verification_code = validation_form.cleaned_data['verification_code']

                if ticket_type == 'activity':
                    ticket = ThemeParkTicket.objects.select_related('visitor', 'event').filter(
                        verification_code=verification_code
                    ).first()
                    if ticket:
                        validation_result = {
                            'kind': 'Activity / Event Ticket',
                            'verification_code': ticket.verification_code,
                            'status': 'Valid ticket record',
                            'guest': ticket.visitor.username if ticket.visitor else 'Entrance guest',
                            'name': ticket.event.name,
                            'quantity': ticket.quantity,
                            'schedule': ticket.event.schedule_label,
                            'event_type': ticket.event.get_event_type_display(),
                            'channel': ticket.get_channel_display(),
                            'purchased': ticket.purchased_at,
                        }
                    else:
                        other_ticket = ThemeParkEntranceTicket.objects.filter(
                            verification_code=verification_code
                        ).first()
                        if other_ticket:
                            validation_error = 'This is an entrance ticket UUID. Change ticket type to Entrance Ticket.'
                        else:
                            validation_error = 'No activity or event ticket found with that verification ID.'
                else:
                    ticket = ThemeParkEntranceTicket.objects.select_related('visitor').filter(
                        verification_code=verification_code
                    ).first()
                    if ticket:
                        validation_result = {
                            'kind': 'Entrance Ticket',
                            'verification_code': ticket.verification_code,
                            'status': 'Valid entrance ticket',
                            'guest': ticket.visitor.username if ticket.visitor else 'Entrance guest',
                            'name': 'Theme Park Entrance',
                            'quantity': ticket.quantity,
                            'schedule': ticket.visit_date,
                            'event_type': 'General admission',
                            'channel': ticket.get_channel_display(),
                            'purchased': ticket.purchased_at,
                        }
                    else:
                        other_ticket = ThemeParkTicket.objects.filter(
                            verification_code=verification_code
                        ).first()
                        if other_ticket:
                            validation_error = 'This is an activity/event ticket UUID. Change ticket type to Activity / Event Ticket.'
                        else:
                            validation_error = 'No entrance ticket found with that verification ID.'

    sold_tickets = tickets.aggregate(total=Sum('quantity'))['total'] or 0
    online_tickets = tickets.filter(channel=ThemeParkTicket.Channel.ONLINE).aggregate(total=Sum('quantity'))['total'] or 0
    entrance_activity_tickets = tickets.filter(channel=ThemeParkTicket.Channel.ENTRANCE).aggregate(total=Sum('quantity'))['total'] or 0
    entrance_admissions = entrance_tickets.aggregate(total=Sum('quantity'))['total'] or 0
    upcoming_events = [
        event for event in events
        if event.schedule_type == Event.ScheduleType.WEEKLY
        or (event.schedule_type == Event.ScheduleType.SPECIAL and event.date and event.date >= timezone.now().date())
    ]
    for event in events:
        if event.capacity:
            event.capacity_percent = min(100, int((event.booked_total / event.capacity) * 100))
        else:
            event.capacity_percent = None
    total_capacity = sum(event.capacity or 0 for event in upcoming_events)
    available_capacity = sum(event.available_capacity or 0 for event in upcoming_events)
    activity_revenue = sum(ticket.quantity * ticket.event.price for ticket in tickets)
    entrance_revenue = sum(ticket.total_price for ticket in entrance_tickets)
    total_revenue = activity_revenue + entrance_revenue
    unique_online_visitors = tickets.filter(visitor__isnull=False).values('visitor').distinct().count()
    unique_entrance_visitors = entrance_tickets.filter(visitor__isnull=False).values('visitor').distinct().count()

    return render(request, 'themepark/staff_dashboard.html', {
        'weekly_event_form': weekly_event_form,
        'special_event_form': special_event_form,
        'activity_ticket_form': activity_ticket_form,
        'entrance_ticket_form': entrance_ticket_form,
        'promotion_form': promotion_form,
        'validation_form': validation_form,
        'validation_result': validation_result,
        'validation_error': validation_error,
        'active_section': active_section,
        'events': events,
        'weekly_events': weekly_events,
        'special_events': special_events,
        'tickets': tickets,
        'entrance_tickets': entrance_tickets,
        'promotions': promotions,
        'upcoming_event_count': len(upcoming_events),
        'total_capacity': total_capacity,
        'available_capacity': available_capacity,
        'sold_tickets': sold_tickets,
        'online_tickets': online_tickets,
        'entrance_activity_tickets': entrance_activity_tickets,
        'entrance_admissions': entrance_admissions,
        'activity_revenue': activity_revenue,
        'entrance_revenue': entrance_revenue,
        'total_revenue': total_revenue,
        'unique_online_visitors': unique_online_visitors,
        'unique_entrance_visitors': unique_entrance_visitors,
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
        if event.available_capacity is not None:
            event.available_capacity -= ticket.quantity
            event.save()


class ThemeParkPromotionViewSet(viewsets.ModelViewSet):
    queryset = ThemeParkPromotion.objects.all()
    serializer_class = ThemeParkPromotionSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.THEMEPARK_STAFF]


class ThemeParkEntranceTicketViewSet(viewsets.ModelViewSet):
    serializer_class = ThemeParkEntranceTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.THEMEPARK_STAFF, User.Role.ADMIN]:
            return ThemeParkEntranceTicket.objects.all().order_by('-purchased_at')
        return ThemeParkEntranceTicket.objects.filter(visitor=user).order_by('-purchased_at')

    def perform_create(self, serializer):
        serializer.save(
            visitor=self.request.user,
            channel=ThemeParkEntranceTicket.Channel.ONLINE,
            price_per_ticket=ENTRANCE_TICKET_PRICE,
        )
