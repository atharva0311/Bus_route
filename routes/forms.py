from django import forms
from buses.models import Route

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
