from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from buses.models import Bus, Route, Trip
from bookings.models import Booking
from tracking.models import LiveLocation

from .serializers import (
    BusSerializer,
    RouteSerializer,
    TripSerializer,
    BookingSerializer,
    LiveLocationSerializer,
)


class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bus.objects.filter(is_active=True)
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class LiveLocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LiveLocation.objects.select_related("bus")
    serializer_class = LiveLocationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

