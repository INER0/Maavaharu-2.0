# Picnic Island Booking System - Backend

Django + Django REST Framework + PostgreSQL.

## Setup
1. Create the database (once):  CREATE DATABASE picnic_island_db;
2. Install packages:  pip install django djangorestframework psycopg2-binary
3. Set your PostgreSQL password before running Django:
   PowerShell:  $env:POSTGRES_PASSWORD="your_password"
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver

Then open http://127.0.0.1:8000/api/ in your browser.

## Apps
- accounts   : custom User with roles + register/login (token auth)
- hotels     : hotels, rooms, bookings, promotions
- ferry      : schedules managed by ferry staff
- themepark  : events (rides/shows/beach) + tickets
- core       : advertisements + island map locations
