from django import forms
from django.utils import timezone
from django.db.models import Sum
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'travel_date',
            'from_stop',
            'to_stop',
            'seats_booked',
            'passenger_name',
            'passenger_phone',
            'passenger_email',
        ]
        widgets = {
            'travel_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # Changed to TextInput and made read-only since there are no intermediate stops
            'from_stop': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'to_stop': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'seats_booked': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'passenger_name': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.bus = kwargs.pop('bus', None)
        super().__init__(*args, **kwargs)

        # Auto-fill the origin and destination based on the new Route model
        if self.bus and self.bus.route:
            self.fields['from_stop'].initial = self.bus.route.origin
            self.fields['to_stop'].initial = self.bus.route.destination

    def clean_travel_date(self):
        date = self.cleaned_data['travel_date']
        if date < timezone.now().date():
            raise forms.ValidationError("Travel date cannot be in the past.")
        return date

    def clean_seats_booked(self):
        seats = self.cleaned_data.get('seats_booked')

        if seats < 1:
            raise forms.ValidationError("At least 1 seat must be booked.")

        if seats > 10:
            raise forms.ValidationError("Maximum 10 seats allowed.")

        return seats

    def clean(self):
        cleaned = super().clean()
        travel_date = cleaned.get('travel_date')
        seats_requested = cleaned.get('seats_booked')

        if not all([travel_date, seats_requested, self.bus]):
            return cleaned

        # -----------------------------
        # SIMPLIFIED SEAT VALIDATION
        # -----------------------------
        # Since we don't have multiple stops, we just check total bookings for this bus on this date
        booked_seats = Booking.objects.filter(
            bus=self.bus,
            travel_date=travel_date,
            status__in=['pending', 'confirmed']
        ).aggregate(total=Sum('seats_booked'))['total'] or 0

        available_seats = self.bus.total_seats - booked_seats

        if seats_requested > available_seats:
            raise forms.ValidationError(
                f"Only {available_seats} seat(s) available for this bus."
            )

        return cleaned
