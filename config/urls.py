from django.contrib import admin
from django.urls import path, include
from accounts.views import account_page, login_page, logout_page, signup_page
from core.views import home
from ferry.views import ferry_page
from hotels.views import hotel_booking_page
from themepark.views import themepark_page

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_page, name='login'),
    path('signup/', signup_page, name='signup'),
    path('logout/', logout_page, name='logout'),
    path('account/', account_page, name='account'),
    path('hotel-booking/', hotel_booking_page, name='hotel_booking'),
    path('ferry/', ferry_page, name='ferry'),
    path('theme-park/', themepark_page, name='themepark'),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('hotels.urls')),
    path('api/', include('ferry.urls')),
    path('api/', include('themepark.urls')),
    path('api/', include('core.urls')),
]
