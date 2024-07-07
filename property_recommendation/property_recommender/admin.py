# admin.py

from django.contrib import admin
from .models import PropertySearch

@admin.register(PropertySearch)
class PropertySearchAdmin(admin.ModelAdmin):
    list_display = ('location', 'bedrooms', 'min_price', 'max_price', 'search_date')
    list_filter = ('location', 'bedrooms', 'search_date')
    search_fields = ('location', 'bedrooms')
