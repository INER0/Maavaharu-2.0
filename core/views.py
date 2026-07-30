from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import redirect, render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from accounts.models import User
from accounts.permissions import ReadOnlyOrStaff
from ferry.models import FerrySchedule
from hotels.models import Hotel, HotelBooking, HotelPromotion, Room
from themepark.models import Event, ThemeParkEntranceTicket, ThemeParkTicket
from .cart import cart_total, complete_checkout, get_cart, remove_item
from .forms import (
    AdminUserUpdateForm, AdvertisementForm, MapImageForm, MapLocationForm, MockPaymentForm,
    SystemIssueForm,
)
from .models import Advertisement, MapImage, MapLocation, SystemIssue
from .serializers import AdvertisementSerializer, MapLocationSerializer


def home(request):
    advertisements = Advertisement.objects.filter(is_active=True).order_by('-created_at')[:3]
    promotions = HotelPromotion.objects.prefetch_related('images').all().order_by('valid_until')[:3]
    hotels = Hotel.objects.prefetch_related('rooms__images').all()[:3]
    events = Event.objects.prefetch_related('images').all().order_by(
        'schedule_type', 'weekday', 'date', 'time'
    )[:4]
    locations = MapLocation.objects.all()[:5]

    return render(request, 'home.html', {
        'advertisements': advertisements,
        'promotions': promotions,
        'hotels': hotels,
        'events': events,
        'locations': locations,
    })


def island_map_page(request):
    locations = MapLocation.objects.all().order_by('category', 'name')
    map_image = MapImage.objects.filter(is_active=True).order_by('-uploaded_at').first()

    return render(request, 'core/map.html', {
        'locations': locations,
        'map_image': map_image,
    })


def _is_system_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == User.Role.ADMIN)


@login_required(login_url='login')
def system_admin_dashboard(request):
    if not _is_system_admin(request.user):
        messages.error(request, 'Only system administrators can access this dashboard.')
        return redirect('home')

    section_choices = {'overview', 'users', 'content', 'map', 'reports', 'issues'}
    active_section = request.GET.get('section', 'overview')
    if active_section not in section_choices:
        active_section = 'overview'

    def admin_section_redirect(section):
        return redirect(f"{request.path}?section={section}")

    users = User.objects.all().order_by('role', 'username')
    advertisements = Advertisement.objects.all().order_by('-created_at')
    locations = MapLocation.objects.all().order_by('category', 'name')
    map_images = MapImage.objects.all().order_by('-uploaded_at')
    issues = SystemIssue.objects.all().order_by('status', '-created_at')

    advertisement_form = AdvertisementForm()
    map_image_form = MapImageForm()
    map_location_form = MapLocationForm()
    issue_form = SystemIssueForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_user':
            active_section = 'users'
            user_record = User.objects.filter(id=request.POST.get('user_id')).first()
            if user_record:
                form = AdminUserUpdateForm(request.POST, instance=user_record)
                if form.is_valid():
                    form.save()
                    messages.success(request, f'{user_record.username} permissions updated.')
                    return admin_section_redirect('users')

        elif action == 'delete_user':
            active_section = 'users'
            user_record = User.objects.filter(id=request.POST.get('user_id')).first()
            if user_record and user_record != request.user:
                username = user_record.username
                user_record.delete()
                messages.success(request, f'{username} account removed.')
                return admin_section_redirect('users')
            messages.error(request, 'You cannot delete your own admin account from here.')

        elif action == 'add_advertisement':
            active_section = 'content'
            advertisement_form = AdvertisementForm(request.POST)
            if advertisement_form.is_valid():
                advertisement_form.save()
                messages.success(request, 'Homepage advertisement added.')
                return admin_section_redirect('content')

        elif action == 'toggle_advertisement':
            active_section = 'content'
            advertisement = Advertisement.objects.filter(id=request.POST.get('advertisement_id')).first()
            if advertisement:
                advertisement.is_active = not advertisement.is_active
                advertisement.save(update_fields=['is_active'])
                messages.success(request, 'Advertisement status updated.')
                return admin_section_redirect('content')

        elif action == 'delete_advertisement':
            active_section = 'content'
            Advertisement.objects.filter(id=request.POST.get('advertisement_id')).delete()
            messages.success(request, 'Advertisement removed.')
            return admin_section_redirect('content')

        elif action == 'add_location':
            active_section = 'map'
            map_location_form = MapLocationForm(request.POST)
            if map_location_form.is_valid():
                map_location_form.save()
                messages.success(request, 'Map location added.')
                return admin_section_redirect('map')

        elif action == 'add_map_image':
            active_section = 'map'
            map_image_form = MapImageForm(request.POST, request.FILES)
            if map_image_form.is_valid():
                map_image = map_image_form.save()
                if map_image.is_active:
                    MapImage.objects.exclude(id=map_image.id).update(is_active=False)
                messages.success(request, 'Public island map image uploaded.')
                return admin_section_redirect('map')

        elif action == 'activate_map_image':
            active_section = 'map'
            map_image = MapImage.objects.filter(id=request.POST.get('map_image_id')).first()
            if map_image:
                MapImage.objects.exclude(id=map_image.id).update(is_active=False)
                map_image.is_active = True
                map_image.save(update_fields=['is_active'])
                messages.success(request, 'Active public map image updated.')
                return admin_section_redirect('map')

        elif action == 'delete_map_image':
            active_section = 'map'
            MapImage.objects.filter(id=request.POST.get('map_image_id')).delete()
            messages.success(request, 'Map image removed.')
            return admin_section_redirect('map')

        elif action == 'delete_location':
            active_section = 'map'
            MapLocation.objects.filter(id=request.POST.get('location_id')).delete()
            messages.success(request, 'Map location removed.')
            return admin_section_redirect('map')

        elif action == 'add_issue':
            active_section = 'issues'
            issue_form = SystemIssueForm(request.POST)
            if issue_form.is_valid():
                issue_form.save()
                messages.success(request, 'System issue logged.')
                return admin_section_redirect('issues')

        elif action == 'update_issue':
            active_section = 'issues'
            issue = SystemIssue.objects.filter(id=request.POST.get('issue_id')).first()
            if issue:
                issue.status = request.POST.get('status', issue.status)
                issue.resolved_at = timezone.now() if issue.status == SystemIssue.Status.RESOLVED else None
                issue.save(update_fields=['status', 'resolved_at'])
                messages.success(request, 'Issue status updated.')
                return admin_section_redirect('issues')

    hotel_revenue = 0
    for booking in HotelBooking.objects.filter(status=HotelBooking.Status.CONFIRMED).select_related('room'):
        nights = max((booking.check_out - booking.check_in).days, 1)
        hotel_revenue += booking.room.price_per_night * booking.num_rooms * nights

    activity_revenue = 0
    for ticket in ThemeParkTicket.objects.select_related('event'):
        activity_revenue += ticket.event.price * ticket.quantity

    entrance_revenue = 0
    for ticket in ThemeParkEntranceTicket.objects.all():
        entrance_revenue += ticket.total_price

    context = {
        'active_section': active_section,
        'users': users,
        'advertisements': advertisements,
        'locations': locations,
        'map_images': map_images,
        'issues': issues,
        'advertisement_form': advertisement_form,
        'map_image_form': map_image_form,
        'map_location_form': map_location_form,
        'issue_form': issue_form,
        'total_users': users.count(),
        'visitor_count': users.filter(role=User.Role.VISITOR).count(),
        'staff_count': users.exclude(role=User.Role.VISITOR).count(),
        'active_ads_count': advertisements.filter(is_active=True).count(),
        'hotel_booking_count': HotelBooking.objects.count(),
        'pending_hotel_count': HotelBooking.objects.filter(status=HotelBooking.Status.PENDING).count(),
        'room_count': Room.objects.count(),
        'event_count': Event.objects.count(),
        'activity_ticket_count': ThemeParkTicket.objects.aggregate(total=Sum('quantity'))['total'] or 0,
        'entrance_ticket_count': ThemeParkEntranceTicket.objects.aggregate(total=Sum('quantity'))['total'] or 0,
        'ferry_schedule_count': FerrySchedule.objects.count(),
        'open_issue_count': issues.exclude(status=SystemIssue.Status.RESOLVED).count(),
        'hotel_revenue': hotel_revenue,
        'activity_revenue': activity_revenue,
        'entrance_revenue': entrance_revenue,
    }
    return render(request, 'core/system_admin_dashboard.html', context)


@login_required(login_url='login')
def cart_page(request):
    items = get_cart(request)

    return render(request, 'core/cart.html', {
        'cart_items': items,
        'cart_total': cart_total(items),
    })


@login_required(login_url='login')
def remove_cart_item(request, item_id):
    if request.method == 'POST':
        remove_item(request, item_id)
        messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@login_required(login_url='login')
def checkout_page(request):
    items = get_cart(request)
    if not items:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart')

    return render(request, 'core/checkout.html', {
        'cart_items': items,
        'cart_total': cart_total(items),
    })


@login_required(login_url='login')
def payment_page(request):
    items = get_cart(request)
    if not items:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        form = MockPaymentForm(request.POST)
        if form.is_valid():
            try:
                complete_checkout(request)
            except ValueError as error:
                messages.error(request, str(error))
                return redirect('checkout')
            messages.success(request, 'Payment completed and your booking records were created.')
            return redirect('checkout_confirmation')
    else:
        form = MockPaymentForm()

    return render(request, 'core/payment.html', {
        'form': form,
        'cart_items': items,
        'cart_total': cart_total(items),
    })


@login_required(login_url='login')
def checkout_confirmation_page(request):
    records = request.session.get('last_checkout_records', [])

    return render(request, 'core/confirmation.html', {
        'records': records,
    })


class AdvertisementViewSet(viewsets.ModelViewSet):
    """Anyone can view ads (even logged-out homepage); admin manages them."""
    queryset = Advertisement.objects.filter(is_active=True)
    serializer_class = AdvertisementSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.ADMIN]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()


class MapLocationViewSet(viewsets.ModelViewSet):
    """Island map points. Public to read; admin maintains them."""
    queryset = MapLocation.objects.all()
    serializer_class = MapLocationSerializer
    permission_classes = [ReadOnlyOrStaff]
    manager_roles = [User.Role.ADMIN]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
