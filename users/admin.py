from django.contrib import admin
from .models import UserProfile, Driver

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'experience_years', 'is_available', 'rating')
    list_filter = ('is_available',)
    search_fields = ('user__username', 'license_number')
