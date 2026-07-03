from django.contrib import admin
from django.urls import path, include
from accounts.views import login_page, logout_page, signup_page
from core.views import home

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_page, name='login'),
    path('signup/', signup_page, name='signup'),
    path('logout/', logout_page, name='logout'),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('hotels.urls')),
    path('api/', include('ferry.urls')),
    path('api/', include('themepark.urls')),
    path('api/', include('core.urls')),
]
