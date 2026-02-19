# from django import forms
# from django.utils import timezone
# from .models import Booking
# from buses.models import Stop


# class BookingForm(forms.ModelForm):
#     class Meta:
#         model = Booking
#         fields = [
#             'travel_date',
#             'from_stop',
#             'to_stop',
#             'seats_booked',
#             'passenger_name',
#             'passenger_phone',
#             'passenger_email'
#         ]
#         widgets = {
#             'travel_date': forms.DateInput(
#                 attrs={'class': 'form-control', 'type': 'date'}
#             ),
#             'from_stop': forms.Select(
#                 attrs={'class': 'form-control'}
#             ),
#             'to_stop': forms.Select(
#                 attrs={'class': 'form-control'}
#             ),
#             'seats_booked': forms.NumberInput(
#                 attrs={'class': 'form-control', 'min': 1, 'max': 10}
#             ),
#             'passenger_name': forms.TextInput(
#                 attrs={'class': 'form-control'}
#             ),
#             'passenger_phone': forms.TextInput(
#                 attrs={'class': 'form-control'}
#             ),
#             'passenger_email': forms.EmailInput(
#                 attrs={'class': 'form-control'}
#             ),
#         }

#     def __init__(self, *args, **kwargs):
#         self.bus = kwargs.pop('bus', None)
#         super().__init__(*args, **kwargs)

#         if self.bus and self.bus.route:
#             self.fields['from_stop'].queryset = Stop.objects.filter(
#                 route=self.bus.route
#             ).order_by('sequence_number')

#             self.fields['to_stop'].queryset = Stop.objects.filter(
#                 route=self.bus.route
#             ).order_by('sequence_number')

#     def clean_travel_date(self):
#         travel_date = self.cleaned_data['travel_date']
#         if travel_date < timezone.now().date():
#             raise forms.ValidationError(
#                 'Travel date cannot be in the past.'
#             )
#         return travel_date

#     def clean(self):
#         cleaned_data = super().clean()
#         from_stop = cleaned_data.get('from_stop')
#         to_stop = cleaned_data.get('to_stop')

#         if from_stop and to_stop:
#             if from_stop.sequence_number >= to_stop.sequence_number:
#                 raise forms.ValidationError(
#                     'Destination stop must be after boarding stop.'
#                 )

#         return cleaned_data

#     def clean_seats_booked(self):
#         seats = self.cleaned_data['seats_booked']
#         if seats < 1:
#             raise forms.ValidationError(
#                 'At least 1 seat must be booked.'
#             )
#         if seats > 10:
#             raise forms.ValidationError(
#                 'Maximum 10 seats can be booked at once.'
#             )
#         return seats


from django import forms
from django.utils import timezone
from django.db.models import Sum
from .models import Booking
from buses.models import Stop


class StopSelect(forms.Select):
    """Custom Select widget that adds data-sequence and data-fare to each <option>."""
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            try:
                stop = Stop.objects.get(pk=int(value))
                option['attrs']['data-sequence'] = stop.sequence_number
                # Added this line to send the price to the frontend
                option['attrs']['data-fare'] = float(stop.fare_from_previous)
            except (Stop.DoesNotExist, ValueError, TypeError):
                pass
        return option

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
            'from_stop': StopSelect(attrs={'class': 'form-control'}),
            'to_stop': StopSelect(attrs={'class': 'form-control'}),
            'seats_booked': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'passenger_name': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.bus = kwargs.pop('bus', None)
        super().__init__(*args, **kwargs)

        if self.bus and self.bus.route:
            qs = Stop.objects.filter(route=self.bus.route).order_by('sequence_number')
            self.fields['from_stop'].queryset = qs
            self.fields['to_stop'].queryset = qs

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

        from_stop = cleaned.get('from_stop')
        to_stop = cleaned.get('to_stop')
        travel_date = cleaned.get('travel_date')
        seats_requested = cleaned.get('seats_booked')

        if not all([from_stop, to_stop, travel_date, seats_requested, self.bus]):
            return cleaned

        # Stop order validation
        if from_stop.sequence_number >= to_stop.sequence_number:
            raise forms.ValidationError(
                "Destination stop must be after boarding stop."
            )

        # -----------------------------
        # SEGMENT-BASED SEAT VALIDATION
        # -----------------------------

        # All stops involved in requested segment
        requested_segment_stops = Stop.objects.filter(
            route=self.bus.route,
            sequence_number__gt=from_stop.sequence_number,
            sequence_number__lte=to_stop.sequence_number
        )

        # Existing bookings for same bus & date
        overlapping_bookings = Booking.objects.filter(
            bus=self.bus,
            travel_date=travel_date,
            status__in=['pending', 'confirmed']
        )

        max_booked_on_any_segment = 0

        for stop in requested_segment_stops:
            booked_on_segment = overlapping_bookings.filter(
                from_stop__sequence_number__lt=stop.sequence_number,
                to_stop__sequence_number__gte=stop.sequence_number,
            ).aggregate(
                total=Sum('seats_booked')
            )['total'] or 0

            if booked_on_segment > max_booked_on_any_segment:
                max_booked_on_any_segment = booked_on_segment

        available_seats = self.bus.total_seats - max_booked_on_any_segment

        if seats_requested > available_seats:
            raise forms.ValidationError(
                f"Only {available_seats} seat(s) available for the selected route segment."
            )

        return cleaned
