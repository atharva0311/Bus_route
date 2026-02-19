from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import UserProfile, Driver
from .forms import UserRegistrationForm, CustomLoginForm, UserProfileForm
from .decorators import role_required


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        UserProfile.objects.create(
            user=self.object,
            role='user',
            phone=form.cleaned_data.get('phone', '')
        )
        messages.success(self.request, 'Registration successful! Please login.')
        return response


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'users/login.html'
    
    def get_success_url(self):
        user = self.request.user

        if user.is_superuser:
            return reverse_lazy('admin_panel:dashboard')

        if hasattr(user, 'profile'):
            if user.profile.role == 'admin':
                return reverse_lazy('admin_panel:dashboard')
            elif user.profile.role == 'driver':
                return reverse_lazy('users:driver_dashboard')

        return reverse_lazy('users:dashboard')


@login_required
def user_dashboard(request):
    user = request.user
    if hasattr(user, 'profile'):
        if user.profile.role == 'admin':
            return redirect('admin_panel:dashboard')
        elif user.profile.role == 'driver':
            return redirect('users:driver_dashboard')
    
    from bookings.models import Booking
    bookings = Booking.objects.filter(user=user).order_by('-booked_at')[:5]
    
    context = {
        'bookings': bookings,
        'total_bookings': Booking.objects.filter(user=user).count(),
        'active_bookings': Booking.objects.filter(user=user, status__in=['pending', 'confirmed']).count(),
    }
    return render(request, 'users/dashboard.html', context)


@login_required
@role_required('driver')
def driver_dashboard(request):
    from buses.models import Bus, Trip
    from django.utils import timezone
    
    driver = get_object_or_404(Driver, user=request.user)
    
    try:
        bus = Bus.objects.get(driver=driver)
        today = timezone.now().date()
        current_trip = Trip.objects.filter(bus=bus, date=today).first()
    except Bus.DoesNotExist:
        bus = None
        current_trip = None
    
    context = {
        'driver': driver,
        'bus': bus,
        'current_trip': current_trip,
    }
    return render(request, 'users/driver_dashboard.html', context)


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'user'}
    )
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'users/profile.html', {'form': form, 'profile': profile})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
