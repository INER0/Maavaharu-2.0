from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('hotels.urls')),
    path('api/', include('ferry.urls')),
    path('api/', include('themepark.urls')),
    path('api/', include('core.urls')),
]
