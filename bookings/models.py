from django.db import models
from django.contrib.auth.models import User
from buses.models import Bus, Trip, Stop, Seat
import uuid

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bookings')
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True)
    travel_date = models.DateField()
    from_stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='bookings_from', null=True, blank=True)
    to_stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='bookings_to', null=True, blank=True)
    seats_booked = models.IntegerField(default=1)
    selected_seats = models.ManyToManyField(Seat, blank=True)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_fare = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    passenger_name = models.CharField(max_length=100)
    passenger_phone = models.CharField(max_length=15)
    passenger_email = models.EmailField(blank=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"

        if self.from_stop_id and self.to_stop_id:
            stops = Stop.objects.filter(
                route=self.bus.route,
                sequence_number__gt=self.from_stop.sequence_number,
                sequence_number__lte=self.to_stop.sequence_number
            )
            self.distance_km = sum(s.distance_from_previous_km for s in stops)
            self.total_fare = sum(s.fare_from_previous for s in stops) * self.seats_booked
        else:
            self.distance_km = 0
            self.total_fare = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.user.username}"

    class Meta:
        ordering = ['-booked_at']


class Payment(models.Model):
    PAYMENT_STATUS = (
        ('created', 'Created'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.status}"
