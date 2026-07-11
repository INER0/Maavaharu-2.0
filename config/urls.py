from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from accounts.views import account_page, login_page, logout_page, signup_page
from core.views import home, island_map_page
from ferry.views import ferry_page, ferry_staff_dashboard
from hotels.views import hotel_booking_page, hotel_staff_dashboard, room_availability
from themepark.views import themepark_page

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_page, name='login'),
    path('signup/', signup_page, name='signup'),
    path('logout/', logout_page, name='logout'),
    path('account/', account_page, name='account'),
    path('hotel-booking/', hotel_booking_page, name='hotel_booking'),
    path('hotel-booking/check-availability/', room_availability, name='room_availability'),
    path('hotel-staff/', hotel_staff_dashboard, name='hotel_staff'),
    path('ferry/', ferry_page, name='ferry'),
    path('ferry-staff/', ferry_staff_dashboard, name='ferry_staff'),
    path('theme-park/', themepark_page, name='themepark'),
    path('map/', island_map_page, name='island_map'),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('hotels.urls')),
    path('api/', include('ferry.urls')),
    path('api/', include('themepark.urls')),
    path('api/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
