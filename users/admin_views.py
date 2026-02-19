from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone

from bookings.models import Booking
from buses.models import Bus, Route, Trip
from buses.forms import BusForm, RouteForm
from tracking.models import LiveLocation
from .models import UserProfile, Driver
from .forms import DriverForm


# -------------------------------------------------
# Admin permission check
# -------------------------------------------------
def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    today = timezone.now().date()

    context = {
        'total_buses': Bus.objects.count(),
        'active_buses': Bus.objects.filter(is_active=True).count(),
        'total_routes': Route.objects.count(),
        'total_drivers': Driver.objects.count(),
        'total_users': UserProfile.objects.filter(role='user').count(),
        'total_bookings': Booking.objects.count(),
        'today_bookings': Booking.objects.filter(travel_date=today).count(),
        'active_trips': Trip.objects.filter(date=today, status='running').count(),
        'recent_bookings': Booking.objects.order_by('-booked_at')[:10],
    }

    return render(request, 'admin_panel/dashboard.html', context)


# -------------------------------------------------
# BUS MANAGEMENT
# -------------------------------------------------
@login_required
@user_passes_test(is_admin)
def bus_list(request):
    buses = Bus.objects.select_related('route', 'driver')
    return render(request, 'admin_panel/bus_list.html', {'buses': buses})


@login_required
@user_passes_test(is_admin)
def bus_add(request):
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus added successfully!')
            return redirect('admin_panel:bus_list')
    else:
        form = BusForm()

    return render(request, 'admin_panel/bus_form.html', {
        'form': form,
        'title': 'Add Bus'
    })


@login_required
@user_passes_test(is_admin)
def bus_edit(request, pk):
    bus = get_object_or_404(Bus, pk=pk)

    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus updated successfully!')
            return redirect('admin_panel:bus_list')
    else:
        form = BusForm(instance=bus)

    return render(request, 'admin_panel/bus_form.html', {
        'form': form,
        'title': 'Edit Bus'
    })


@login_required
@user_passes_test(is_admin)
def bus_delete(request, pk):
    bus = get_object_or_404(Bus, pk=pk)

    if request.method == 'POST':
        bus.delete()
        messages.success(request, 'Bus deleted successfully!')
        return redirect('admin_panel:bus_list')

    return render(request, 'admin_panel/confirm_delete.html', {
        'object': bus,
        'type': 'Bus'
    })


# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@login_required
@user_passes_test(is_admin)
def route_list(request):
    routes = Route.objects.all()
    return render(request, 'admin_panel/route_list.html', {'routes': routes})


@login_required
@user_passes_test(is_admin)
def route_add(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route added successfully!')
            return redirect('admin_panel:route_list')
    else:
        form = RouteForm()

    return render(request, 'admin_panel/route_form.html', {
        'form': form,
        'title': 'Add Route'
    })


@login_required
@user_passes_test(is_admin)
def route_edit(request, pk):
    route = get_object_or_404(Route, pk=pk)

    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route updated successfully!')
            return redirect('admin_panel:route_list')
    else:
        form = RouteForm(instance=route)

    return render(request, 'admin_panel/route_form.html', {
        'form': form,
        'title': 'Edit Route'
    })


@login_required
@user_passes_test(is_admin)
def route_delete(request, pk):
    route = get_object_or_404(Route, pk=pk)

    if request.method == 'POST':
        route.delete()
        messages.success(request, 'Route deleted successfully!')
        return redirect('admin_panel:route_list')

    return render(request, 'admin_panel/confirm_delete.html', {
        'object': route,
        'type': 'Route'
    })


# -------------------------------------------------
# DRIVERS
# -------------------------------------------------
@login_required
@user_passes_test(is_admin)
def driver_list(request):
    drivers = Driver.objects.select_related('user')
    return render(request, 'admin_panel/driver_list.html', {'drivers': drivers})


@login_required
@user_passes_test(is_admin)
def driver_add(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )

            UserProfile.objects.create(user=user, role='driver')

            driver = form.save(commit=False)
            driver.user = user
            driver.save()

            messages.success(request, 'Driver added successfully!')
            return redirect('admin_panel:driver_list')
    else:
        form = DriverForm()

    return render(request, 'admin_panel/driver_form.html', {
        'form': form,
        'title': 'Add Driver'
    })


@login_required
@user_passes_test(is_admin)
def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)

    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            user = driver.user
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']

            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])

            user.save()
            form.save()

            messages.success(request, 'Driver updated successfully!')
            return redirect('admin_panel:driver_list')
    else:
        form = DriverForm(instance=driver)

    return render(request, 'admin_panel/driver_form.html', {
        'form': form,
        'title': 'Edit Driver'
    })


@login_required
@user_passes_test(is_admin)
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)

    if request.method == 'POST':
        user = driver.user
        driver.delete()
        user.delete()
        messages.success(request, 'Driver deleted successfully!')
        return redirect('admin_panel:driver_list')

    return render(request, 'admin_panel/confirm_delete.html', {
        'object': driver,
        'type': 'Driver'
    })


# -------------------------------------------------
# USERS
# -------------------------------------------------
@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = UserProfile.objects.filter(role='user').select_related('user')
    return render(request, 'admin_panel/user_list.html', {'users': users})


# -------------------------------------------------
# BOOKINGS
# -------------------------------------------------
@login_required
@user_passes_test(is_admin)
def booking_list(request):
    bookings = Booking.objects.select_related('user', 'bus').order_by('-booked_at')
    return render(request, 'admin_panel/booking_list.html', {'bookings': bookings})


# -------------------------------------------------
# LIVE TRACKING (ADMIN VIEW)
# -------------------------------------------------
@login_required
@user_passes_test(is_admin)
def live_tracking(request):
    today = timezone.now().date()

    active_buses = Bus.objects.filter(
        is_active=True,
        trips__status='running',
        trips__date=today
    ).distinct()

    bus_locations = []

    for bus in active_buses:
        latest_location = LiveLocation.objects.filter(bus=bus).order_by('-timestamp').first()
        if latest_location:
            bus_locations.append({
                'bus': bus,
                'location': latest_location
            })

    return render(request, 'admin_panel/live_tracking.html', {
        'bus_locations': bus_locations
    })


# -------------------------------------------------
# ANALYTICS
# -------------------------------------------------
@login_required
@user_passes_test(is_admin)
def analytics(request):
    today = timezone.now().date()

    booking_stats = Booking.objects.values('status').annotate(count=Count('id'))

    trip_stats = Trip.objects.filter(
        date__gte=today - timezone.timedelta(days=30)
    ).values('status').annotate(count=Count('id'))

    daily_bookings = (
        Booking.objects
        .filter(booked_at__date__gte=today - timezone.timedelta(days=7))
        .extra({'date': 'date(booked_at)'})
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    return render(request, 'admin_panel/analytics.html', {
        'booking_stats': booking_stats,
        'trip_stats': trip_stats,
        'daily_bookings': list(daily_bookings),
    })
