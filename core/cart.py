from decimal import Decimal
from datetime import date
from uuid import uuid4

from django.db import transaction

from hotels.models import HotelBooking, HotelPromotion, Room
from themepark.models import Event, ThemeParkEntranceTicket, ThemeParkPromotion, ThemeParkTicket


ENTRANCE_TICKET_PRICE = Decimal('100.00')


def _money(value):
    return f'{Decimal(value):.2f}'


def _discounted_total(original_total, promotion):
    original_total = Decimal(original_total)
    if not promotion or not promotion.discount_percent:
        return original_total, Decimal('0.00')

    discount_amount = original_total * Decimal(promotion.discount_percent) / Decimal('100')
    total = max(original_total - discount_amount, Decimal('0.00'))
    return total, discount_amount


def _best_hotel_discount(room):
    return HotelPromotion.objects.filter(
        hotel=room.hotel,
        discount_percent__isnull=False,
        valid_until__gte=date.today(),
    ).order_by('-discount_percent', 'valid_until').first()


def _best_event_discount(event):
    return ThemeParkPromotion.objects.filter(
        event=event,
        discount_percent__isnull=False,
        valid_until__gte=date.today(),
    ).order_by('-discount_percent', 'valid_until').first()


def get_cart(request):
    return request.session.setdefault('cart', [])


def cart_count(request):
    return len(get_cart(request))


def cart_total(items):
    return sum(Decimal(item['total']) for item in items)


def add_item(request, item):
    cart = get_cart(request)
    item['id'] = uuid4().hex
    cart.append(item)
    request.session['cart'] = cart
    request.session.modified = True


def remove_item(request, item_id):
    request.session['cart'] = [
        item for item in get_cart(request)
        if item.get('id') != item_id
    ]
    request.session.modified = True


def clear_cart(request):
    request.session['cart'] = []
    request.session.modified = True


def add_hotel_booking(request, cleaned_data):
    room = cleaned_data['room']
    check_in = cleaned_data['check_in']
    check_out = cleaned_data['check_out']
    nights = max((check_out - check_in).days, 1)
    num_rooms = cleaned_data['num_rooms']
    original_total = room.price_per_night * num_rooms * nights
    promotion = _best_hotel_discount(room)
    total, discount_amount = _discounted_total(original_total, promotion)

    add_item(request, {
        'type': 'hotel',
        'title': f'{room.room_type} room booking',
        'description': f'{check_in} to {check_out}, {num_rooms} room(s), {nights} night(s)',
        'original_total': _money(original_total),
        'discount_percent': promotion.discount_percent if promotion else None,
        'discount_amount': _money(discount_amount),
        'promotion_title': promotion.title if promotion else '',
        'total': _money(total),
        'payload': {
            'room_id': room.id,
            'check_in': check_in.isoformat(),
            'check_out': check_out.isoformat(),
            'num_rooms': num_rooms,
            'adults': cleaned_data['adults'],
            'kids': cleaned_data['kids'],
            'special_requests': cleaned_data.get('special_requests') or '',
        },
    })


def add_entrance_ticket(request, cleaned_data):
    quantity = cleaned_data['quantity']
    total = ENTRANCE_TICKET_PRICE * quantity

    add_item(request, {
        'type': 'entrance',
        'title': 'Theme Park Entrance Ticket',
        'description': f'{quantity} ticket(s), visit date {cleaned_data["visit_date"]}',
        'total': _money(total),
        'payload': {
            'visit_date': cleaned_data['visit_date'].isoformat(),
            'quantity': quantity,
            'price_per_ticket': _money(ENTRANCE_TICKET_PRICE),
        },
    })


def add_themepark_ticket(request, cleaned_data):
    event = cleaned_data['event']
    quantity = cleaned_data['quantity']
    original_total = event.price * quantity
    promotion = _best_event_discount(event)
    total, discount_amount = _discounted_total(original_total, promotion)

    add_item(request, {
        'type': 'activity',
        'title': event.name,
        'description': f'{event.get_event_type_display()} | {event.schedule_label} | {quantity} ticket(s)',
        'original_total': _money(original_total),
        'discount_percent': promotion.discount_percent if promotion else None,
        'discount_amount': _money(discount_amount),
        'promotion_title': promotion.title if promotion else '',
        'total': _money(total),
        'payload': {
            'event_id': event.id,
            'quantity': quantity,
        },
    })


@transaction.atomic
def complete_checkout(request):
    created_records = []

    for item in get_cart(request):
        item_type = item['type']
        payload = item['payload']

        if item_type == 'hotel':
            room = Room.objects.select_for_update().get(id=payload['room_id'])
            check_in = date.fromisoformat(payload['check_in'])
            check_out = date.fromisoformat(payload['check_out'])
            available_rooms = room.available_rooms(check_in, check_out)
            if payload['num_rooms'] > available_rooms:
                raise ValueError(f'Only {available_rooms} room(s) are available for {room.room_type}.')

            booking = HotelBooking.objects.create(
                visitor=request.user,
                room=room,
                check_in=check_in,
                check_out=check_out,
                num_rooms=payload['num_rooms'],
                adults=payload['adults'],
                kids=payload['kids'],
                special_requests=payload['special_requests'],
                status=HotelBooking.Status.CONFIRMED,
            )
            created_records.append({
                'kind': 'Hotel Booking',
                'verification_code': str(booking.verification_code),
                'title': str(room),
                'description': f'{booking.check_in} to {booking.check_out}',
            })

        elif item_type == 'entrance':
            ticket = ThemeParkEntranceTicket.objects.create(
                visitor=request.user,
                visit_date=payload['visit_date'],
                quantity=payload['quantity'],
                price_per_ticket=payload['price_per_ticket'],
                channel=ThemeParkEntranceTicket.Channel.ONLINE,
            )
            created_records.append({
                'kind': 'Entrance Ticket',
                'verification_code': str(ticket.verification_code),
                'title': 'Theme Park Entrance',
                'description': f'{ticket.quantity} ticket(s), visit date {ticket.visit_date}',
            })

        elif item_type == 'activity':
            event = Event.objects.select_for_update().get(id=payload['event_id'])
            quantity = payload['quantity']
            if event.available_capacity is not None and quantity > event.available_capacity:
                raise ValueError(f'Only {event.available_capacity} spot(s) are left for {event.name}.')

            ticket = ThemeParkTicket.objects.create(
                visitor=request.user,
                event=event,
                quantity=quantity,
                channel=ThemeParkTicket.Channel.ONLINE,
            )
            if event.available_capacity is not None:
                event.available_capacity -= quantity
                event.save()

            created_records.append({
                'kind': 'Activity Ticket',
                'verification_code': str(ticket.verification_code),
                'title': event.name,
                'description': event.schedule_label,
            })

    clear_cart(request)
    request.session['last_checkout_records'] = created_records
    request.session.modified = True
    return created_records
