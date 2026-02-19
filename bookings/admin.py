from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id',
        'user',
        'bus',
        'travel_date',
        'from_stop',
        'to_stop',
        'seats_booked',
        'total_fare',
        'status',
        'booked_at',
    )

    list_filter = (
        'status',
        'travel_date',
        'bus',
    )

    search_fields = (
        'booking_id',
        'user__username',
        'passenger_name',
        'passenger_phone',
    )

    readonly_fields = (
        'booking_id',
        'distance_km',
        'total_fare',
        'booked_at',
    )

    fieldsets = (
        ("Booking Info", {
            "fields": (
                'booking_id',
                'status',
                'user',
                'bus',
                'trip',
                'travel_date',
            )
        }),
        ("Route", {
            "fields": (
                'from_stop',
                'to_stop',
            )
        }),
        ("Seats", {
            "fields": (
                'seats_booked',
                'selected_seats',
            )
        }),
        ("Passenger Details", {
            "fields": (
                'passenger_name',
                'passenger_phone',
                'passenger_email',
            )
        }),
        ("Fare Calculation", {
            "fields": (
                'distance_km',
                'total_fare',
            )
        }),
    )
