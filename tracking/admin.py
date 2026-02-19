from django.contrib import admin
from .models import LiveLocation, ETACalculation


@admin.register(LiveLocation)
class LiveLocationAdmin(admin.ModelAdmin):
    list_display = (
        'bus',
        'latitude',
        'longitude',
        'speed_kmh',
        'timestamp',
    )
    list_filter = ('bus',)
    ordering = ('-timestamp',)


@admin.register(ETACalculation)
class ETACalculationAdmin(admin.ModelAdmin):
    list_display = (
        'bus',
        'destination_name',
        'distance_remaining_km',
        'estimated_arrival_time',
    )
    list_filter = ('bus',)
