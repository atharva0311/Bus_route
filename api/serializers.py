from rest_framework import serializers
from buses.models import Bus, Route, Trip
from bookings.models import Booking
from tracking.models import LiveLocation


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"


class BusSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)

    class Meta:
        model = Bus
        fields = "__all__"


class TripSerializer(serializers.ModelSerializer):
    bus = BusSerializer(read_only=True)

    class Meta:
        model = Trip
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    bus = BusSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"


class LiveLocationSerializer(serializers.ModelSerializer):
    bus = BusSerializer(read_only=True)

    class Meta:
        model = LiveLocation
        fields = "__all__"
