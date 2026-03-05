from django.contrib import admin
from .models import Car, Booking

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'model_year', 'transmission', 'car_type', 'price', 'created_at')
    search_fields = ('brand', 'name', 'car_type')
    list_filter = ('transmission', 'car_type', 'model_year')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'start_date', 'end_date', 'booked_at')
    search_fields = ('user__username', 'vehicle__name')
    list_filter = ('start_date', 'end_date')
