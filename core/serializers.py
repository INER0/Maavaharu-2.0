from rest_framework import serializers
from .models import Advertisement, MapLocation


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'content', 'image_url', 'is_active', 'created_at']


class MapLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapLocation
        fields = ['id', 'name', 'category', 'description', 'latitude', 'longitude']
