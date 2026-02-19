from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('users/', include('users.urls')),
    path('buses/', include('buses.urls')),
    path('bookings/', include('bookings.urls')),
    path('tracking/', include('tracking.urls')),
    path('api/', include('api.urls')),

    # ✅ ADMIN PANEL
    path('admin-panel/', include([
        path('', include('users.admin_urls')),
        path('routes/', include('routes.urls')),   # ✅ FIX
    ])),
]
