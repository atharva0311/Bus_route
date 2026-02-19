from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required

from geopy.distance import geodesic
import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import LiveLocation, ETACalculation
from buses.models import Bus, Trip
from users.decorators import driver_required


# =====================================================
# DRIVER → SEND GPS LOCATION
# =====================================================
@login_required
@driver_required
@csrf_exempt
@require_POST
def update_location(request):
    try:
        data = json.loads(request.body)

        bus_id = data.get("bus_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        speed = float(data.get("speed", 0))
        heading = float(data.get("heading", 0))

        if not all([bus_id, latitude, longitude]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        bus = get_object_or_404(Bus, id=bus_id)
        today = timezone.now().date()
        trip = Trip.objects.filter(bus=bus, date=today).first()

        location = LiveLocation.objects.create(
            bus=bus,
            trip=trip,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed,
            heading=heading,
        )

        next_stop = None
        eta_time = None

        if bus.route:
            stops = bus.route.stops.order_by("sequence_number")

            for stop in stops:
                stop_pos = (float(stop.latitude), float(stop.longitude))
                dist = geodesic((latitude, longitude), stop_pos).km

                if dist > 0.05:
                    next_stop = stop
                    speed_used = speed if speed > 5 else 40
                    minutes = (dist / speed_used) * 60
                    eta_time = timezone.now() + timezone.timedelta(minutes=minutes)
                    break

        # Save ETA
        if next_stop and trip:
            ETACalculation.objects.update_or_create(
                bus=bus,
                trip=trip,
                destination_name=next_stop.name,
                defaults={
                    "destination_latitude": next_stop.latitude,
                    "destination_longitude": next_stop.longitude,
                    "distance_remaining_km": dist,
                    "estimated_arrival_time": eta_time,
                },
            )

        # WebSocket broadcast
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "live_buses",
            {
                "type": "send_location",
                "bus_id": bus.id,
                "bus_name": bus.bus_name,
                "latitude": float(latitude),
                "longitude": float(longitude),
                "speed": speed,
                "route": str(bus.route) if bus.route else "",
                "next_stop": next_stop.name if next_stop else None,
                "eta": eta_time.isoformat() if eta_time else None,
            },
        )

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# =====================================================
# GET SINGLE BUS LIVE DATA
# =====================================================
@require_GET
def get_bus_location(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)

    latest = LiveLocation.objects.filter(bus=bus).order_by("-timestamp").first()
    if not latest:
        return JsonResponse({"error": "No location found"}, status=404)

    eta = ETACalculation.objects.filter(bus=bus).order_by("-id").first()

    data = {
        "bus_id": bus.id,
        "bus_name": bus.bus_name,
        "latitude": float(latest.latitude),
        "longitude": float(latest.longitude),
        "speed": float(latest.speed_kmh),
        "timestamp": latest.timestamp.isoformat(),
    }

    if eta:
        data["eta"] = {
            "destination": eta.destination_name,
            "distance_remaining_km": float(eta.distance_remaining_km),
            "estimated_arrival": eta.estimated_arrival_time.isoformat(),
        }

    return JsonResponse(data)


# =====================================================
# GET ALL ACTIVE BUSES (MAP VIEW)
# =====================================================
@require_GET
def get_all_active_buses(request):
    today = timezone.now().date()
    trips = Trip.objects.filter(date=today, status="running").select_related("bus")

    result = []

    for trip in trips:
        loc = LiveLocation.objects.filter(bus=trip.bus).order_by("-timestamp").first()
        if not loc:
            continue

        eta = ETACalculation.objects.filter(bus=trip.bus).order_by("-id").first()

        item = {
            "bus_id": trip.bus.id,
            "bus_name": trip.bus.bus_name,
            "bus_number": trip.bus.bus_number,
            "latitude": float(loc.latitude),
            "longitude": float(loc.longitude),
            "speed": float(loc.speed_kmh),
            "status": trip.status,
        }

        if eta:
            item["eta"] = {
                "destination": eta.destination_name,
                "distance_remaining_km": float(eta.distance_remaining_km),
                "estimated_arrival": eta.estimated_arrival_time.isoformat(),
            }

        result.append(item)

    return JsonResponse({"buses": result})


# =====================================================
# START TRIP
# =====================================================
@login_required
@driver_required
@csrf_exempt
@require_POST
def start_trip(request):
    data = json.loads(request.body)
    bus_id = data.get("bus_id")

    bus = get_object_or_404(Bus, id=bus_id)
    today = timezone.now().date()

    trip, _ = Trip.objects.get_or_create(
        bus=bus,
        date=today,
        defaults={
            "status": "running",
            "actual_departure_time": timezone.now(),
        },
    )

    trip.status = "running"
    trip.actual_departure_time = timezone.now()
    trip.save()

    return JsonResponse({"status": "success", "trip_id": trip.id})


# =====================================================
# END TRIP
# =====================================================
@login_required
@driver_required
@csrf_exempt
@require_POST
def end_trip(request):
    data = json.loads(request.body)
    trip_id = data.get("trip_id")

    trip = get_object_or_404(Trip, id=trip_id)
    trip.status = "completed"
    trip.actual_arrival_time = timezone.now()
    trip.save()

    return JsonResponse({"status": "success"})


# =====================================================
# DRIVER DASHBOARD
# =====================================================
@login_required
@driver_required
def driver_tracking_view(request):
    from users.models import Driver

    driver = get_object_or_404(Driver, user=request.user)
    bus = Bus.objects.filter(driver=driver).first()
    today = timezone.now().date()

    trip = Trip.objects.filter(bus=bus, date=today).first() if bus else None

    return render(
        request,
        "tracking/driver_tracking.html",
        {
            "driver": driver,
            "bus": bus,
            "current_trip": trip,
        },
    )
