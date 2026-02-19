from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.db import models
from datetime import datetime
from .models import Bus, Route, Stop, Trip


class BusSearchView(ListView):
    model = Bus
    template_name = 'buses/search.html'
    context_object_name = 'buses'
    
    def get_queryset(self):
        queryset = Bus.objects.filter(is_active=True).select_related('route', 'driver')
        
        source = self.request.GET.get('source', '')
        destination = self.request.GET.get('destination', '')
        travel_date = self.request.GET.get('date', '')
        bus_type = self.request.GET.get('bus_type', '')
        
        if source:
            queryset = queryset.filter(route__source__icontains=source)
        if destination:
            queryset = queryset.filter(route__destination__icontains=destination)
        if bus_type:
            queryset = queryset.filter(bus_type=bus_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['routes'] = Route.objects.filter(is_active=True)
        context['search_params'] = {
            'source': self.request.GET.get('source', ''),
            'destination': self.request.GET.get('destination', ''),
            'date': self.request.GET.get('date', ''),
            'bus_type': self.request.GET.get('bus_type', ''),
        }
        return context


class BusDetailView(DetailView):
    model = Bus
    template_name = 'buses/detail.html'
    context_object_name = 'bus'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bus = self.get_object()
        today = timezone.now().date()
        
        context['current_trip'] = Trip.objects.filter(bus=bus, date=today).first()
        
        if bus.route:
            context['stops'] = bus.route.stops.all()
        
        return context


# ==========================
# EXISTING API
# ==========================
def get_routes_json(request):
    routes = Route.objects.filter(is_active=True).values('id', 'source', 'destination', 'name')
    return JsonResponse(list(routes), safe=False)


def get_available_seats(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)
    date_str = request.GET.get('date', '')

    try:
        travel_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()
    except ValueError:
        travel_date = timezone.now().date()

    from bookings.models import Booking
    booked_seats = Booking.objects.filter(
        bus=bus,
        travel_date=travel_date,
        status__in=['confirmed', 'pending']
    ).aggregate(total=models.Sum('seats_booked'))['total'] or 0

    available = bus.total_seats - booked_seats

    return JsonResponse({
        'bus_id': bus_id,
        'total_seats': bus.total_seats,
        'booked_seats': booked_seats,
        'available_seats': available
    })


# ==================================================
# ✅ NEW API 1: Fare Preview API
# ==================================================
def fare_preview_api(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)

    source = request.GET.get('source')
    destination = request.GET.get('destination')

    base_fare = getattr(bus, "base_fare", 0)

    # Simple fallback logic (safe even if stop pricing not implemented)
    multiplier = 1
    if source and destination and source != destination:
        multiplier = 1.0

    estimated_fare = base_fare * multiplier

    return JsonResponse({
        "bus_id": bus.id,
        "source": source,
        "destination": destination,
        "estimated_fare": estimated_fare
    })


# ==================================================
# ✅ NEW API 2: Live GPS Tracking API
# ==================================================
def live_location_api(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)

    today = timezone.now().date()
    trip = Trip.objects.filter(bus=bus, date=today).first()

    # Safe attribute access (won't crash even if fields don't exist)
    latitude = getattr(trip, "current_latitude", None)
    longitude = getattr(trip, "current_longitude", None)
    last_updated = getattr(trip, "location_updated_at", None)

    return JsonResponse({
        "bus_id": bus.id,
        "trip_id": trip.id if trip else None,
        "latitude": latitude,
        "longitude": longitude,
        "last_updated": last_updated,
        "status": getattr(trip, "status", None)
    })
