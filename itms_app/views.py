from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter, OpenApiTypes
from .models import (
    Category, Location, Vendor, Asset, MaintenanceRecord,
    SoftwareLicense, SoftwareInstallation, HelpDeskTicket
)
from .serializers import (
    CategorySerializer, LocationSerializer, VendorSerializer, AssetSerializer,
    MaintenanceRecordSerializer, SoftwareLicenseSerializer,
    SoftwareInstallationSerializer, HelpDeskTicketSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Category.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Location.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Vendor.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            # Allow read operations for authenticated users
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Allow write operations for authenticated users
            # You can add more specific permissions here if needed
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Custom create logic - you can add any business logic here
        """
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Custom update logic - you can add any business logic here
        """
        serializer.save()

    def get_queryset(self):
        queryset = Asset.objects.all()
        
        # Filter parameters
        category = self.request.query_params.get('category', None)
        status = self.request.query_params.get('status', None)
        location = self.request.query_params.get('location', None)
        assigned_to = self.request.query_params.get('assigned_to', None)
        search = self.request.query_params.get('search', None)

        if category is not None:
            queryset = queryset.filter(category__id=category)
        if status is not None:
            queryset = queryset.filter(status=status)
        if location is not None:
            queryset = queryset.filter(location__id=location)
        if assigned_to is not None:
            queryset = queryset.filter(assigned_to__id=assigned_to)
        if search is not None:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(asset_tag__icontains=search) |
                Q(serial_number__icontains=search) |
                Q(model__icontains=search)
            )

        return queryset

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        status_counts = {}
        for status_choice in Asset.ASSET_STATUS_CHOICES:
            status = status_choice[0]
            count = Asset.objects.filter(status=status).count()
            status_counts[status] = count
        return Response(status_counts)


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = MaintenanceRecord.objects.all()
        asset = self.request.query_params.get('asset', None)
        maintenance_type = self.request.query_params.get('maintenance_type', None)
        
        if asset is not None:
            queryset = queryset.filter(asset__id=asset)
        if maintenance_type is not None:
            queryset = queryset.filter(maintenance_type=maintenance_type)
            
        return queryset


class SoftwareLicenseViewSet(viewsets.ModelViewSet):
    queryset = SoftwareLicense.objects.all()
    serializer_class = SoftwareLicenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SoftwareLicense.objects.all()
        name = self.request.query_params.get('name', None)
        vendor = self.request.query_params.get('vendor', None)
        
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        if vendor is not None:
            queryset = queryset.filter(vendor__id=vendor)
            
        return queryset

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        from datetime import date, timedelta
        thirty_days = date.today() + timedelta(days=30)
        expiring_licenses = SoftwareLicense.objects.filter(
            expiry_date__lte=thirty_days,
            expiry_date__gte=date.today()
        )
        serializer = self.get_serializer(expiring_licenses, many=True)
        return Response(serializer.data)


class SoftwareInstallationViewSet(viewsets.ModelViewSet):
    queryset = SoftwareInstallation.objects.all()
    serializer_class = SoftwareInstallationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SoftwareInstallation.objects.all()
        software = self.request.query_params.get('software', None)
        asset = self.request.query_params.get('asset', None)
        
        if software is not None:
            queryset = queryset.filter(software_license__id=software)
        if asset is not None:
            queryset = queryset.filter(asset__id=asset)
            
        return queryset


class HelpDeskTicketViewSet(viewsets.ModelViewSet):
    queryset = HelpDeskTicket.objects.all()
    serializer_class = HelpDeskTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = HelpDeskTicket.objects.all()
        status = self.request.query_params.get('status', None)
        priority = self.request.query_params.get('priority', None)
        assigned_to = self.request.query_params.get('assigned_to', None)
        requester = self.request.query_params.get('requester', None)
        
        if status is not None:
            queryset = queryset.filter(status=status)
        if priority is not None:
            queryset = queryset.filter(priority=priority)
        if assigned_to is not None:
            queryset = queryset.filter(assigned_to__id=assigned_to)
        if requester is not None:
            queryset = queryset.filter(requester__id=requester)
            
        return queryset

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        stats = {}
        for status_choice in HelpDeskTicket.STATUS_CHOICES:
            status = status_choice[0]
            count = HelpDeskTicket.objects.filter(status=status).count()
            stats[status] = count
        return Response(stats)