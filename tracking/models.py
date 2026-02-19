from django.db import models
from buses.models import Bus, Trip


class LiveLocation(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name='locations'
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='locations',
        null=True,
        blank=True
    )

    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    speed_kmh = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    heading = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus} @ {self.latitude}, {self.longitude}"

    class Meta:
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'


class ETACalculation(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name='eta_calculations'
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='eta_calculations',
        null=True,
        blank=True
    )

    destination_name = models.CharField(max_length=200)
    destination_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    destination_longitude = models.DecimalField(max_digits=10, decimal_places=7)

    distance_remaining_km = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_arrival_time = models.DateTimeField()
    calculated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bus} ETA → {self.destination_name}"

    class Meta:
        ordering = ['-calculated_at']
