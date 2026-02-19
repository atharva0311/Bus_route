from django import forms
from .models import Bus, Route, Stop

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = [
            'bus_number', 'bus_name', 'bus_type', 'total_seats',
            'route', 'driver', 'departure_time', 'arrival_time',
            'amenities', 'is_active'
        ]
        widgets = {
            'bus_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bus_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bus_type': forms.Select(attrs={'class': 'form-select'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'route': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'arrival_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'source', 'destination', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class StopForm(forms.ModelForm):
    class Meta:
        model = Stop
        fields = [
            'route', 'name', 'latitude', 'longitude',
            'sequence_number', 'estimated_arrival_offset_minutes'
        ]
        widgets = {
            'route': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0000001'}),
            'sequence_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'estimated_arrival_offset_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
        }
