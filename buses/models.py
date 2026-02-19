from django.db import models
from users.models import Driver


class Route(models.Model):
    name = models.CharField(max_length=200)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} → {self.destination}"

    @property
    def total_distance_km(self):
        return self.stops.aggregate(
            total=models.Sum('distance_from_previous_km')
        )['total'] or 0

    class Meta:
        ordering = ['source', 'destination']


class Stop(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='stops'
    )
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    sequence_number = models.IntegerField()

    distance_from_previous_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    fare_from_previous = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    estimated_arrival_offset_minutes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Stop {self.sequence_number})"

    class Meta:
        ordering = ['route', 'sequence_number']
        unique_together = ['route', 'sequence_number']


class Bus(models.Model):
    BUS_TYPE_CHOICES = [
        ('ac', 'AC'),
        ('non_ac', 'Non-AC'),
        ('sleeper', 'Sleeper'),
        ('semi_sleeper', 'Semi-Sleeper'),
    ]

    bus_number = models.CharField(max_length=20, unique=True)
    bus_name = models.CharField(max_length=100)
    bus_type = models.CharField(
        max_length=20,
        choices=BUS_TYPE_CHOICES,
        default='ac'
    )
    total_seats = models.IntegerField(default=40)

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        related_name='buses'
    )

    driver = models.OneToOneField(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bus'
    )

    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    amenities = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus_name} ({self.bus_number})"

    # ✅ SEGMENT-WISE SEAT AVAILABILITY
    def seats_available_between(self, from_stop, to_stop, date):
        from bookings.models import Booking

        overlapping = Booking.objects.filter(
            bus=self,
            travel_date=date,
            status__in=['pending', 'confirmed'],
            from_stop__sequence_number__lt=to_stop.sequence_number,
            to_stop__sequence_number__gt=from_stop.sequence_number,
        )

        booked = overlapping.aggregate(
            models.Sum('seats_booked')
        )['seats_booked__sum'] or 0

        return max(self.total_seats - booked, 0)

    class Meta:
        verbose_name_plural = "Buses"


class Trip(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('running', 'Running'),
        ('delayed', 'Delayed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name='trips'
    )
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started'
    )

    actual_departure_time = models.DateTimeField(null=True, blank=True)
    actual_arrival_time = models.DateTimeField(null=True, blank=True)
    delay_minutes = models.IntegerField(default=0)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['bus', 'date']
        ordering = ['-date']


class PerformanceMetrics(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    date = models.DateField()
    total_trips = models.IntegerField(default=0)
    on_time_trips = models.IntegerField(default=0)
    delayed_trips = models.IntegerField(default=0)
    cancelled_trips = models.IntegerField(default=0)
    total_passengers = models.IntegerField(default=0)
    average_delay_minutes = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"{self.bus} - {self.date}"


# ✅ SEAT MODEL (NEW — SAFE ADDITION)
class Seat(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name="seats"
    )
    seat_number = models.CharField(max_length=5)
    is_window = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bus.bus_number} - {self.seat_number}"
