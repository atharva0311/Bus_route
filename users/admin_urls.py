from django.urls import path
from . import admin_views

app_name = 'admin_panel'

urlpatterns = [
    path('', admin_views.admin_dashboard, name='dashboard'),
    path('buses/', admin_views.bus_list, name='bus_list'),
    path('buses/add/', admin_views.bus_add, name='bus_add'),
    path('buses/<int:pk>/edit/', admin_views.bus_edit, name='bus_edit'),
    path('buses/<int:pk>/delete/', admin_views.bus_delete, name='bus_delete'),

    # path('routes/', admin_views.route_list, name='route_list'),
    # path('routes/add/', admin_views.route_add, name='route_add'),
    # path('routes/<int:pk>/edit/', admin_views.route_edit, name='route_edit'),
    # path('routes/<int:pk>/delete/', admin_views.route_delete, name='route_delete'),

    path('drivers/', admin_views.driver_list, name='driver_list'),
    path('drivers/add/', admin_views.driver_add, name='driver_add'),
    path('drivers/<int:pk>/edit/', admin_views.driver_edit, name='driver_edit'),
    path('drivers/<int:pk>/delete/', admin_views.driver_delete, name='driver_delete'),

    path('users/', admin_views.user_list, name='user_list'),

    path('bookings/', admin_views.booking_list, name='booking_list'),

    path('live-tracking/', admin_views.live_tracking, name='live_tracking'),
    
    path('analytics/', admin_views.analytics, name='analytics'),
]
