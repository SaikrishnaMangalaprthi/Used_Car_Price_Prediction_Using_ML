from django.contrib import admin
from .models import UserProfile, PredictionHistory

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'email']
    list_editable = ['is_active']

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'brand', 'vehicle_age', 'predicted_price', 'created_at']
    list_filter = ['fuel_type', 'transmission_type']