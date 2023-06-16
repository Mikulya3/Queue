from rest_framework import serializers
from .models import Television, Terminal, MobileApp, Website

class TelevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Television
        fields = ('id', 'brand', 'model', 'screen_size', 'resolution', 'smart_tv', 'wifi_enabled')


class TerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = ('id', 'name', 'type', 'software_version', 'is_active')


class MobileAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileApp
        fields = ('id', 'name', 'version', 'platform', 'developer', 'release_date')


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ('id', 'name', 'url', 'description', 'is_active')