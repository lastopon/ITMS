from rest_framework import serializers
from .models import (
    Category, Location, Vendor, Asset, MaintenanceRecord,
    SoftwareLicense, SoftwareInstallation, HelpDeskTicket
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class AssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    class Meta:
        model = Asset
        fields = '__all__'


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = '__all__'


class SoftwareLicenseSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    available_installations = serializers.IntegerField(read_only=True)

    class Meta:
        model = SoftwareLicense
        fields = '__all__'


class SoftwareInstallationSerializer(serializers.ModelSerializer):
    software_name = serializers.CharField(source='software_license.name', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    installed_by_name = serializers.CharField(source='installed_by.get_full_name', read_only=True)

    class Meta:
        model = SoftwareInstallation
        fields = '__all__'


class HelpDeskTicketSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)

    class Meta:
        model = HelpDeskTicket
        fields = '__all__'