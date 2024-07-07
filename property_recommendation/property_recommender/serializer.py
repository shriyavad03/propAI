# serializers.py
from rest_framework import serializers
from .models import PropertySearch

class DailyPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertySearch
        fields = ['search_date', 'max_price', 'min_price']
