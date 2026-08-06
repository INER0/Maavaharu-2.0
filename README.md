# Maavaharu Booking System

Maavaharu is a Django web application for an island hotel, ferry schedule information, and nearby theme park booking system. Visitors can book hotel rooms, buy entrance/activity tickets, view promotions, use the island map, and manage bookings from their account page. Staff dashboards are included for hotel staff, ferry operators, theme park staff, and system administrators.

## Tech Stack

- Python
- Django 5.2.5
- Django REST Framework
- PostgreSQL
- Pillow for uploaded images
- HTML, CSS, and Django templates

## Main Features

- Visitor registration and login
- Hotel room browsing and booking
- Room availability checking by date range
- Cart, checkout, payment, and confirmation screens
- Theme park entrance tickets
- Theme park activities, shows, and beach event tickets
- Ticket and booking verification codes using UUIDs
- Ferry schedule information for visitors
- Interactive island map with uploaded map image, clickable pins, coordinates, and location photos
- Dynamic advertisements and promotions
- Separate dashboards for hotel staff, ferry operators, theme park staff, and system administrators

## Staff Areas

- `/hotel-staff/` - manage Maavaharu Hotel rooms, bookings, availability, and promotions
- `/ferry-staff/` - manage ferry schedules and validate hotel booking eligibility
- `/theme-park-staff/` - manage activities, events, tickets, capacity, promotions, and ticket validation
- `/system-admin/` - manage users, advertisements, map content, reports, and system issues

## Visitor Pages

- `/` - homepage
- `/login/` - login
- `/signup/` - create visitor account
- `/account/` - visitor bookings and tickets
- `/hotel-booking/` - Maavaharu Hotel booking
- `/ferry/` - ferry schedule information
- `/theme-park/` - theme park tickets, activities, shows, and beach events
- `/map/` - island map
- `/cart/` - cart
- `/checkout/` - checkout

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install requirements:

```powershell
pip install -r requirements.txt
```

3. Create the PostgreSQL database:

```sql
CREATE DATABASE picnic_island_db;
```

4. Check the database settings in `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'picnic_island_db',
        'USER': 'postgres',
        'PASSWORD': 'pass123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

5. Run migrations:

```powershell
python manage.py migrate
```

6. Start the server:

```powershell
python manage.py runserver
```

7. Open the site:

```text
http://127.0.0.1:8000/
```

## Useful Test Accounts

These accounts may exist in the local development database:

- System admin: `systemadmin` / `pass123`
- Theme park staff: `themeparkstaff` / `ThemePark123`

If an account does not exist, create it from the Django admin or the system admin dashboard.

## API

The API routes are mounted under `/api/` for:

- accounts
- hotels
- ferry
- theme park
- core map and advertisements

## Notes

- The app uses a custom user model: `accounts.User`.
- Uploaded media is stored in the `media/` folder during development.
- Static files are stored in the `static/` folder.
- Visitor-facing pages use `static/css/style.css`.
- Staff/admin dashboards use separate staff/admin styling.
