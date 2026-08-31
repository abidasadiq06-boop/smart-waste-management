from django.contrib import admin
from .models import Citizen, WasteRequest

@admin.register(Citizen)
class CitizenAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name', 'phone')

@admin.register(WasteRequest)
class WasteRequestAdmin(admin.ModelAdmin):
    list_display = ('citizen', 'waste_type', 'status', 'calculated_amount', 'is_paid', 'created_at')
    list_filter = ('waste_type', 'status', 'is_paid')
    search_fields = ('citizen__name', 'scrap_category')