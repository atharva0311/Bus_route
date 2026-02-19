from django.urls import path
from . import views

app_name = "tracking"

urlpatterns = [
    path("api/update-location/", views.update_location, name="update_location"),
    path("api/bus/<int:bus_id>/", views.get_bus_location, name="get_bus_location"),
    path("api/active-buses/", views.get_all_active_buses, name="get_active_buses"),

    path("api/trip/start/", views.start_trip, name="start_trip"),
    path("api/trip/end/", views.end_trip, name="end_trip"),

    path("driver/", views.driver_tracking_view, name="driver_view"),
]
