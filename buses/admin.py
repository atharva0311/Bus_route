from django.contrib import admin
from .models import (
    Route,
    Stop,
    Bus,
    Seat,
    Trip,
    PerformanceMetrics,
)


class StopInline(admin.TabularInline):
    model = Stop
    extra = 1
    ordering = ['sequence_number']
    fields = (
        'sequence_number',
        'name',
        'latitude',
        'longitude',
        'distance_from_previous_km',
        'fare_from_previous',
        'estimated_arrival_offset_minutes',
    )


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'source', 'destination', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'source', 'destination')
    inlines = [StopInline]


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 4
    fields = ('seat_number', 'is_window')


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = (
        'bus_name',
        'bus_number',
        'bus_type',
        'route',
        'total_seats',
        'is_active',
    )
    list_filter = ('bus_type', 'is_active')
    search_fields = ('bus_name', 'bus_number')
    inlines = [SeatInline]


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'bus',
        'date',
        'status',
        'actual_departure_time',
        'actual_arrival_time',
    )
    list_filter = ('status', 'date')
    search_fields = ('bus__bus_number',)


@admin.register(PerformanceMetrics)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = (
        'bus',
        'date',
        'total_trips',
        'on_time_trips',
        'delayed_trips',
        'cancelled_trips',
        'average_delay_minutes',
    )
    list_filter = ('date', 'bus')
