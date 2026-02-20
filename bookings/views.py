from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db import models
from .models import Booking, Payment
from .forms import BookingForm
from buses.models import Bus, Trip, Seat
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
import uuid
import paypalrestsdk
import os
import google.generativeai as genai

# Configure PayPal lazily — only when credentials are available
_paypal_configured = False

def _ensure_paypal_configured():
    global _paypal_configured
    if not _paypal_configured and settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET:
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_MODE,
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET,
        })
        _paypal_configured = True

@login_required
def book_bus(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id, is_active=True)
    travel_date = request.GET.get('date', timezone.now().date())

    if request.method == 'POST':
        form = BookingForm(request.POST, bus=bus)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.bus = bus

            trip, _ = Trip.objects.get_or_create(
                bus=bus,
                date=booking.travel_date,
                defaults={'status': 'not_started'}
            )
            booking.trip = trip
            booking.save()
            messages.success(request, f"Booking created! Booking ID: {booking.booking_id}")
            return redirect('bookings:create_payment', booking_id=booking.pk)
    else:
        form = BookingForm(
            bus=bus,
            initial={
                'travel_date': travel_date,
                'passenger_name': request.user.get_full_name() or request.user.username,
                'passenger_email': request.user.email,
            }
        )

    return render(request, 'bookings/book.html', {'form': form, 'bus': bus})

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings/list.html', {'bookings': bookings})

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/detail.html', {'booking': booking})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status != 'pending':
        messages.error(request, "This booking cannot be cancelled.")
        return redirect('bookings:detail', pk=pk)

    booking.status = 'cancelled'
    booking.save()
    messages.success(request, "Booking cancelled successfully.")
    return redirect('bookings:list')

@login_required
def track_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/track.html', {'booking': booking})


# ------------------------------
# Seat availability API
# ------------------------------
def booking_seat_status_api(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)
    date = request.GET.get("date", timezone.now().date())
    total = bus.total_seats
    booked = Booking.objects.filter(
        bus=bus,
        travel_date=date,
        status__in=["confirmed", "pending"]
    ).aggregate(models.Sum("seats_booked"))["seats_booked__sum"] or 0

    return JsonResponse({
        "bus_id": bus.id,
        "total_seats": total,
        "booked_seats": booked,
        "available_seats": total - booked
    })

@require_GET
def seat_layout_api(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)
    date = request.GET.get("date")
    booked_seats = Booking.objects.filter(
        bus=bus,
        travel_date=date,
        status__in=["pending", "confirmed"]
    ).values_list("selected_seats__id", flat=True)

    seats = Seat.objects.filter(bus=bus).order_by("seat_number")
    data = {
        "bus_id": bus.id,
        "seats": [
            {"id": seat.id, "number": seat.seat_number, "is_booked": seat.id in booked_seats}
            for seat in seats
        ]
    }
    return JsonResponse(data)


# ------------------------------
# PayPal Payment integration
# ------------------------------
@login_required
def create_payment(request, booking_id):
    _ensure_paypal_configured()

    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        messages.error(request, "PayPal is not configured. Please contact the administrator.")
        return redirect("bookings:detail", pk=booking_id)

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != "pending":
        messages.error(request, "This booking cannot be paid for (invalid state).")
        return redirect("bookings:detail", pk=booking_id)

    # Ensure fare is not zero — PayPal rejects $0 payments
    fare = booking.total_fare
    if not fare or fare <= 0:
        # If fare is 0 (stops have no fare set), confirm booking directly
        booking.status = "confirmed"
        booking.save()
        messages.success(request, f"Booking {booking.booking_id} confirmed! (No payment required)")
        return redirect("bookings:detail", pk=booking.pk)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse("bookings:payment_success")),
            "cancel_url": request.build_absolute_uri(reverse("bookings:payment_cancel")),
        },
        "transactions": [{
            "item_list": {"items": [{
                "name": f"Booking {booking.booking_id}",
                "sku": f"{booking.booking_id}",
                "price": str(fare),
                "currency": "USD",
                "quantity": 1
            }]},
            "amount": {"total": str(fare), "currency": "USD"},
            "description": f"Payment for booking {booking.booking_id}"
        }]
    })

    if payment.create():
        Payment.objects.create(
            booking=booking,
            order_id=payment.id,
            amount=fare,
            status="created"
        )
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)

    # Show actual PayPal error
    error_detail = getattr(payment, 'error', 'Unknown error')
    messages.error(request, f"PayPal error: {error_detail}")
    return redirect("bookings:detail", pk=booking.pk)


@login_required
def payment_success(request):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")

    _ensure_paypal_configured()
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        payment_obj = get_object_or_404(Payment, order_id=payment.id)
        payment_obj.status = "success"
        payment_obj.payment_id = payment.id
        payment_obj.save()

        booking = payment_obj.booking
        booking.status = "confirmed"
        booking.save()
        messages.success(request, f"Payment successful! Booking ID: {booking.booking_id}")
        return redirect("bookings:detail", pk=booking.id)
    else:
        messages.error(request, "Payment failed")
        return redirect("bookings:list")


@login_required
def payment_cancel(request):
    messages.warning(request, "Payment cancelled")
    return redirect("bookings:list")
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Grab the secret key from Render's hidden vault!
my_secret_key = os.getenv("GEMINI_API_KEY")

if my_secret_key:
    genai.configure(api_key=my_secret_key)

@csrf_exempt 
def chat_with_gemini(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            model = genai.GenerativeModel(
               'gemini-2.5-flash',
                system_instruction="You are a helpful customer support chatbot for the KMT Bus Booking system. You help passengers check schedules, book tickets, and explain MSBTE student concession passes. Keep your answers brief and friendly."
            )
            
            response = model.generate_content(user_message)
            return JsonResponse({'reply': response.text, 'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'error': str(e), 'status': 'failed'}, status=500)
            
    return JsonResponse({'error': 'Only POST requests allowed'}, status=400)
