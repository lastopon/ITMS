from django.contrib import admin
from django.apps import apps
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    # Core Asset Management
    Category, Location, Vendor, Asset, MaintenanceRecord,
    SoftwareLicense, SoftwareInstallation,
    
    # Service Management  
    HelpDeskTicket, Reservation, ServiceCatalog, ServiceRequest, ChangeManagement,
    
    # Security & Compliance
    SecurityIncident, VulnerabilityAssessment, AccessControlMatrix, SecurityAuditLog,
    ComplianceFramework, ComplianceRequirement, AuditRecord,
    
    # Infrastructure & Network
    NetworkDevice, IPAddressAllocation, NetworkPort, NetworkMonitoring,
    BackupPolicy, BackupJob, DisasterRecoveryPlan, DisasterRecoveryTest,
    
    # Inventory & Procurement
    InventoryItem, PurchaseRequest, PurchaseRequestItem,
    
    # Monitoring & Analytics
    SystemMonitoring, Alert, AlertRule, Report, ReportGeneration,
    
    # Mobile & Device Management
    MobileDevice, MobileAppManagement, MobileSecurityPolicy,
    
    # Knowledge & Training
    KnowledgeBase, TrainingRecord
)

# Custom app labels for organized admin grouping
def get_app_display_name(app_label):
    """Get display name for app label"""
    app_names = {
        'itms_app': 'ITMS - IT Management System',
        'accounts': 'User Management',
        'auth': 'Authentication & Authorization'
    }
    return app_names.get(app_label, app_label.title())

# Configure admin site
admin.site.site_header = "ITMS Administration"
admin.site.site_title = "ITMS Admin"
admin.site.index_title = "IT Management System"

# ==============================================================================
# 🏢 ASSET & INVENTORY MANAGEMENT - การจัดการทรัพย์สินและคลังสินค้า
# ==============================================================================
class AssetInventoryAdminMixin:
    """Base admin configuration for asset and inventory management"""
    list_per_page = 25
    save_on_top = True
    
    class Meta:
        app_label = 'Asset & Inventory Management'
        verbose_name_plural = 'Asset & Inventory Management'

@admin.register(Category)
class CategoryAdmin(AssetInventoryAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Location)
class LocationAdmin(AssetInventoryAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'address', 'created_at']
    search_fields = ['name', 'address']
    list_filter = ['created_at']

@admin.register(Vendor)
class VendorAdmin(AssetInventoryAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone']
    search_fields = ['name', 'contact_person', 'email']
    list_filter = ['created_at']

# Temporarily disable complex Asset admin
# @admin.register(Asset)
class AssetAdminComplex(AssetInventoryAdminMixin, admin.ModelAdmin):
    """Comprehensive Asset management admin interface"""
    
    # List display with enhanced fields
    list_display = [
        'asset_tag', 'name', 'category', 'status_display', 'condition', 
        'location', 'assigned_to', 'warranty_status', 'purchase_cost'
    ]
    
    # Enhanced list filters
    list_filter = [
        'category', 'status', 'condition', 'location', 
        'manufacturer', 'vendor', 'created_at', 'purchase_date', 'warranty_expiry'
    ]
    
    # Enhanced search capabilities
    search_fields = [
        'asset_tag', 'name', 'serial_number', 'model', 
        'manufacturer', 'barcode', 'notes'
    ]
    
    # Autocomplete for foreign keys
    autocomplete_fields = ['assigned_to', 'vendor']
    
    # Date hierarchy
    date_hierarchy = 'created_at'
    
    # Readonly fields
    readonly_fields = ['created_at', 'updated_at', 'current_value', 'warranty_status']
    
    def get_readonly_fields(self, request, obj=None):
        """Make timestamp fields readonly only when editing existing objects"""
        if obj:  # Editing existing asset
            return self.readonly_fields
        else:  # Adding new asset
            return []
    
    def get_fieldsets(self, request, obj=None):
        """Use add_fieldsets when adding new assets, regular fieldsets when editing"""
        if not obj and hasattr(self, 'add_fieldsets'):
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
    
    # Enhanced fieldsets for better organization
    fieldsets = (
        ('📋 Basic Information', {
            'fields': (
                ('asset_tag', 'barcode'),
                ('name', 'category'),
                'description',
                'asset_image'
            ),
            'description': 'Essential asset identification and categorization'
        }),
        
        ('🔧 Technical Specifications', {
            'fields': (
                ('manufacturer', 'model'),
                ('serial_number', 'condition'),
            ),
            'classes': ('collapse',),
            'description': 'Hardware and technical details'
        }),
        
        ('💰 Financial Information', {
            'fields': (
                ('vendor', 'purchase_date'),
                ('purchase_cost', 'depreciation_rate'),
                'warranty_expiry'
            ),
            'classes': ('collapse',),
            'description': 'Cost, warranty, and financial tracking'
        }),
        
        ('📊 Financial Analysis', {
            'fields': (
                ('current_value',),
            ),
            'classes': ('collapse',),
            'description': 'Calculated financial values'
        }),
        
        ('📍 Location & Assignment', {
            'fields': (
                ('location', 'assigned_to'),
                'status'
            ),
            'description': 'Current location and responsible person'
        }),
        
        ('🛡️ Status Information', {
            'fields': (
                ('warranty_status',),
            ),
            'classes': ('collapse',),
            'description': 'Auto-calculated status fields'
        }),
        
        ('📝 Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        
        ('🕐 Timestamps', {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('collapse',)
        })
    )
    
    # Add fieldsets specifically for creating new assets
    add_fieldsets = (
        ('📋 Essential Information', {
            'fields': (
                ('name', 'category'),
                'description',
            ),
            'description': 'Required information to create a new asset'
        }),
        
        ('🏷️ Identification', {
            'fields': (
                ('asset_tag', 'barcode'),
                ('serial_number', 'model'),
                'manufacturer'
            ),
            'classes': ('collapse',),
            'description': 'Asset identification and technical details (optional)'
        }),
        
        ('📍 Location & Assignment', {
            'fields': (
                'location',
                ('assigned_to', 'status'),
                'condition'
            ),
            'description': 'Where is this asset located and who is responsible?'
        }),
        
        ('💰 Financial Information', {
            'fields': (
                ('vendor', 'purchase_date'),
                ('purchase_cost', 'depreciation_rate'),
                'warranty_expiry'
            ),
            'classes': ('collapse',),
            'description': 'Purchase and financial details (optional)'
        }),
        
        ('📝 Additional Details', {
            'fields': (
                'asset_image',
                'notes'
            ),
            'classes': ('collapse',),
            'description': 'Optional additional information'
        })
    )
    
    # Actions for bulk operations
    actions = [
        'make_active', 'make_inactive', 'send_to_maintenance',
        'retire_assets', 'update_location', 'generate_asset_report'
    ]
    
    # Custom display methods
    def status_display(self, obj):
        """Enhanced status display with colors"""
        status_colors = {
            'active': '#28a745',
            'inactive': '#dc3545',
            'maintenance': '#ffc107',
            'retired': '#6c757d',
            'disposed': '#343a40'
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = '🔄 Status'
    status_display.admin_order_field = 'status'
    
    def warranty_status(self, obj):
        """Display warranty status"""
        if not obj.warranty_expiry:
            return '❓ Unknown'
        
        today = timezone.now().date()
        if obj.warranty_expiry < today:
            return format_html('<span style="color: #dc3545;">❌ Expired</span>')
        elif (obj.warranty_expiry - today).days <= 30:
            return format_html('<span style="color: #ffc107;">⚠️ Expiring Soon</span>')
        else:
            return format_html('<span style="color: #28a745;">✅ Valid</span>')
    warranty_status.short_description = '🛡️ Warranty'
    
    def current_value(self, obj):
        """Calculate current depreciated value"""
        if not obj.purchase_cost or not obj.purchase_date or not obj.depreciation_rate:
            return 'N/A'
        
        today = timezone.now().date()
        years_owned = (today - obj.purchase_date).days / 365.25
        depreciation_amount = (obj.purchase_cost * obj.depreciation_rate / 100) * years_owned
        current_val = max(0, obj.purchase_cost - depreciation_amount)
        
        return f'${current_val:,.2f}'
    current_value.short_description = '💰 Current Value'
    
    # Custom actions
    def make_active(self, request, queryset):
        """Set selected assets as active"""
        count = queryset.update(status='active')
        self.message_user(request, f'{count} assets have been set to active.')
    make_active.short_description = '🟢 Set as Active'
    
    def make_inactive(self, request, queryset):
        """Set selected assets as inactive"""
        count = queryset.update(status='inactive')
        self.message_user(request, f'{count} assets have been set to inactive.')
    make_inactive.short_description = '🔴 Set as Inactive'
    
    def send_to_maintenance(self, request, queryset):
        """Send selected assets to maintenance"""
        count = queryset.update(status='maintenance')
        self.message_user(request, f'{count} assets have been sent to maintenance.')
    send_to_maintenance.short_description = '🔧 Send to Maintenance'
    
    def retire_assets(self, request, queryset):
        """Retire selected assets"""
        count = queryset.update(status='retired')
        self.message_user(request, f'{count} assets have been retired.')
    retire_assets.short_description = '📦 Retire Assets'
    
    def get_queryset(self, request):
        """Optimize queryset with related fields"""
        return super().get_queryset(request).select_related(
            'category', 'location', 'assigned_to', 'vendor'
        )
    
    def save_model(self, request, obj, form, change):
        """Add custom save logic if needed"""
        # Auto-generate asset tag if not provided
        if not obj.asset_tag and not change:
            from datetime import datetime
            year = datetime.now().year
            count = Asset.objects.filter(created_at__year=year).count() + 1
            obj.asset_tag = f'ITMS-{year}-{count:04d}'
        
        super().save_model(request, obj, form, change)

# Enhanced Asset admin with proper configuration
@admin.register(Asset)
class AssetAdmin(AssetInventoryAdminMixin, admin.ModelAdmin):
    """Enhanced Asset management admin interface"""
    
    # List display with essential fields
    list_display = [
        'asset_tag', 'name', 'category', 'status_display', 'condition', 
        'location', 'assigned_to', 'purchase_cost'
    ]
    
    # List filters
    list_filter = [
        'category', 'status', 'condition', 'location', 
        'manufacturer', 'vendor', 'created_at'
    ]
    
    # Search capabilities
    search_fields = [
        'asset_tag', 'name', 'serial_number', 'model', 
        'manufacturer', 'barcode', 'notes'
    ]
    
    # Autocomplete for foreign keys
    autocomplete_fields = ['assigned_to', 'vendor']
    
    # Date hierarchy
    date_hierarchy = 'created_at'
    
    # Readonly fields for editing
    readonly_fields = ['created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        """Make timestamp fields readonly only when editing existing objects"""
        if obj:  # Editing existing asset
            return self.readonly_fields
        else:  # Adding new asset - exclude readonly fields completely
            return []
    
    def get_fieldsets(self, request, obj=None):
        """Use different fieldsets for add vs edit to handle readonly fields"""
        if obj:  # Editing existing asset
            return self.fieldsets
        else:  # Adding new asset - exclude timestamp fieldset
            return (
                ('📋 Basic Information (Required)', {
                    'fields': (
                        'name',
                        'category', 
                        'location',
                        ('asset_tag', 'barcode'),
                        'description',
                        'asset_image'
                    ),
                    'description': 'Required fields: Name, Category, Location. Asset tag will be auto-generated if empty.'
                }),
                
                ('🔧 Technical Specifications', {
                    'fields': (
                        ('manufacturer', 'model'),
                        ('serial_number', 'condition'),
                    ),
                    'classes': ('collapse',),
                    'description': 'Hardware and technical details'
                }),
                
                ('💰 Financial Information', {
                    'fields': (
                        ('vendor', 'purchase_date'),
                        ('purchase_cost', 'depreciation_rate'),
                        'warranty_expiry'
                    ),
                    'classes': ('collapse',),
                    'description': 'Cost, warranty, and financial tracking'
                }),
                
                ('📍 Assignment & Status', {
                    'fields': (
                        'assigned_to',
                        ('status', 'condition')
                    ),
                    'classes': ('collapse',),
                    'description': 'Who is responsible and current status'
                }),
                
                ('📝 Additional Information', {
                    'fields': ('notes',),
                    'classes': ('collapse',)
                })
            )
    
    # Enhanced fieldsets for better organization (editing existing assets)
    fieldsets = (
        ('📋 Basic Information', {
            'fields': (
                ('asset_tag', 'barcode'),
                ('name', 'category'),
                'description',
                'asset_image'
            ),
            'description': 'Essential asset identification and categorization'
        }),
        
        ('🔧 Technical Specifications', {
            'fields': (
                ('manufacturer', 'model'),
                ('serial_number', 'condition'),
            ),
            'classes': ('collapse',),
            'description': 'Hardware and technical details'
        }),
        
        ('💰 Financial Information', {
            'fields': (
                ('vendor', 'purchase_date'),
                ('purchase_cost', 'depreciation_rate'),
                'warranty_expiry'
            ),
            'classes': ('collapse',),
            'description': 'Cost, warranty, and financial tracking'
        }),
        
        ('📍 Location & Assignment', {
            'fields': (
                ('location', 'assigned_to'),
                'status'
            ),
            'description': 'Current location and responsible person'
        }),
        
        ('📝 Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        
        ('🕐 Timestamps', {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('collapse',)
        })
    )
    
    # Actions for bulk operations
    actions = [
        'make_active', 'make_inactive', 'send_to_maintenance', 'retire_assets'
    ]
    
    # Custom display methods
    def status_display(self, obj):
        """Enhanced status display with colors"""
        status_colors = {
            'active': '#28a745',
            'inactive': '#dc3545',
            'maintenance': '#ffc107',
            'retired': '#6c757d',
            'disposed': '#343a40'
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = '🔄 Status'
    status_display.admin_order_field = 'status'
    
    # Custom actions
    def make_active(self, request, queryset):
        """Set selected assets as active"""
        count = queryset.update(status='active')
        self.message_user(request, f'{count} assets have been set to active.')
    make_active.short_description = '🟢 Set as Active'
    
    def make_inactive(self, request, queryset):
        """Set selected assets as inactive"""
        count = queryset.update(status='inactive')
        self.message_user(request, f'{count} assets have been set to inactive.')
    make_inactive.short_description = '🔴 Set as Inactive'
    
    def send_to_maintenance(self, request, queryset):
        """Send selected assets to maintenance"""
        count = queryset.update(status='maintenance')
        self.message_user(request, f'{count} assets have been sent to maintenance.')
    send_to_maintenance.short_description = '🔧 Send to Maintenance'
    
    def retire_assets(self, request, queryset):
        """Retire selected assets"""
        count = queryset.update(status='retired')
        self.message_user(request, f'{count} assets have been retired.')
    retire_assets.short_description = '📦 Retire Assets'
    
    def get_queryset(self, request):
        """Optimize queryset with related fields"""
        return super().get_queryset(request).select_related(
            'category', 'location', 'assigned_to', 'vendor'
        )
    
    def save_model(self, request, obj, form, change):
        """Add custom save logic"""
        # Auto-generate asset tag if not provided
        if not obj.asset_tag and not change:
            from datetime import datetime
            year = datetime.now().year
            count = Asset.objects.filter(created_at__year=year).count() + 1
            obj.asset_tag = f'ITMS-{year}-{count:04d}'
        
        super().save_model(request, obj, form, change)

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(AssetInventoryAdminMixin, admin.ModelAdmin):
    list_display = ['asset', 'maintenance_type', 'maintenance_date', 'performed_by', 'cost']
    list_filter = ['maintenance_type', 'maintenance_date', 'performed_by']
    search_fields = ['asset__name', 'asset__asset_tag']
    date_hierarchy = 'maintenance_date'
    raw_id_fields = ['asset', 'performed_by']

@admin.register(SoftwareLicense)
class SoftwareLicenseAdmin(AssetInventoryAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'version', 'vendor', 'max_installations', 'expiry_date']
    list_filter = ['vendor', 'expiry_date']
    search_fields = ['name', 'version']
    raw_id_fields = ['vendor']

@admin.register(SoftwareInstallation)
class SoftwareInstallationAdmin(AssetInventoryAdminMixin, admin.ModelAdmin):
    list_display = ['software_license', 'asset', 'installed_by', 'installation_date']
    list_filter = ['installation_date', 'installed_by']
    search_fields = ['software_license__name', 'asset__name']
    raw_id_fields = ['software_license', 'asset', 'installed_by']

# ==============================================================================
# 🛠️ SERVICE MANAGEMENT - การจัดการบริการ
# ==============================================================================
class ServiceManagementAdminMixin:
    """Base admin configuration for service management"""
    list_per_page = 20
    save_on_top = True

@admin.register(HelpDeskTicket)
class HelpDeskTicketAdmin(ServiceManagementAdminMixin, admin.ModelAdmin):
    list_display = ['ticket_number', 'title', 'priority', 'status', 'requester', 'assigned_to']
    list_filter = ['priority', 'status', 'category', 'created_at']
    search_fields = ['ticket_number', 'title', 'description']
    readonly_fields = ['ticket_number', 'created_at']
    raw_id_fields = ['requester', 'assigned_to', 'asset']

@admin.register(Reservation)
class ReservationAdmin(ServiceManagementAdminMixin, admin.ModelAdmin):
    list_display = ['reservation_number', 'title', 'asset', 'reserved_by', 'status', 'start_datetime']
    list_filter = ['status', 'reservation_type', 'start_datetime']
    search_fields = ['reservation_number', 'title']
    readonly_fields = ['reservation_number']
    raw_id_fields = ['asset', 'reserved_by', 'approved_by']

@admin.register(ServiceCatalog)
class ServiceCatalogAdmin(ServiceManagementAdminMixin, admin.ModelAdmin):
    list_display = ['service_code', 'service_name', 'service_type', 'service_owner', 'status']
    list_filter = ['service_type', 'status']
    search_fields = ['service_code', 'service_name']
    raw_id_fields = ['service_owner']

@admin.register(ServiceRequest)
class ServiceRequestAdmin(ServiceManagementAdminMixin, admin.ModelAdmin):
    list_display = ['request_number', 'service', 'requested_by', 'priority', 'status']
    list_filter = ['service', 'priority', 'status']
    search_fields = ['request_number', 'title']
    readonly_fields = ['request_number']
    raw_id_fields = ['service', 'requested_by', 'requested_for', 'assigned_to', 'approved_by']

@admin.register(ChangeManagement)
class ChangeManagementAdmin(ServiceManagementAdminMixin, admin.ModelAdmin):
    list_display = ['change_number', 'title', 'change_type', 'risk_level', 'status', 'requested_by']
    list_filter = ['change_type', 'risk_level', 'status']
    search_fields = ['change_number', 'title']
    readonly_fields = ['change_number']
    filter_horizontal = ['affected_services', 'affected_assets']
    raw_id_fields = ['requested_by', 'assigned_to', 'approved_by']

# ==============================================================================
# 🔒 SECURITY & COMPLIANCE - ความปลอดภัยและการปฏิบัติตาม
# ==============================================================================
class SecurityComplianceAdminMixin:
    """Base admin configuration for security and compliance"""
    list_per_page = 15
    save_on_top = True
    
    class Meta:
        app_label = 'Security & Compliance'
        verbose_name_plural = 'Security & Compliance'

@admin.register(SecurityIncident)
class SecurityIncidentAdmin(SecurityComplianceAdminMixin, admin.ModelAdmin):
    list_display = ['incident_id', 'title', 'incident_type', 'severity', 'status', 'reported_by']
    list_filter = ['incident_type', 'severity', 'status', 'discovered_date']
    search_fields = ['incident_id', 'title']
    readonly_fields = ['incident_id']
    filter_horizontal = ['affected_assets']
    raw_id_fields = ['reported_by', 'assigned_to']

@admin.register(VulnerabilityAssessment)
class VulnerabilityAssessmentAdmin(SecurityComplianceAdminMixin, admin.ModelAdmin):
    list_display = ['vulnerability_id', 'title', 'cve_id', 'risk_level', 'status', 'discovered_by']
    list_filter = ['risk_level', 'status', 'discovery_date']
    search_fields = ['vulnerability_id', 'title', 'cve_id']
    readonly_fields = ['vulnerability_id']
    filter_horizontal = ['affected_assets']
    raw_id_fields = ['discovered_by', 'assigned_to']

@admin.register(AccessControlMatrix)
class AccessControlMatrixAdmin(SecurityComplianceAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'asset', 'access_type', 'granted_by', 'granted_date', 'is_active']
    list_filter = ['access_type', 'is_active', 'granted_date']
    search_fields = ['user__username', 'asset__name']
    raw_id_fields = ['user', 'asset', 'granted_by']

@admin.register(SecurityAuditLog)
class SecurityAuditLogAdmin(SecurityComplianceAdminMixin, admin.ModelAdmin):
    list_display = ['timestamp', 'event_type', 'user', 'asset', 'outcome', 'risk_level']
    list_filter = ['event_type', 'outcome', 'risk_level', 'timestamp']
    search_fields = ['user__username', 'asset__name']
    readonly_fields = ['timestamp']
    raw_id_fields = ['user', 'asset']

@admin.register(ComplianceFramework)
class ComplianceFrameworkAdmin(SecurityComplianceAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'version', 'effective_date', 'next_review_date', 'responsible_person', 'is_active']
    list_filter = ['is_active', 'effective_date']
    search_fields = ['name', 'version']
    raw_id_fields = ['responsible_person']

@admin.register(ComplianceRequirement)
class ComplianceRequirementAdmin(SecurityComplianceAdminMixin, admin.ModelAdmin):
    list_display = ['framework', 'control_id', 'title', 'status', 'responsible_person']
    list_filter = ['framework', 'status']
    search_fields = ['control_id', 'title']
    raw_id_fields = ['framework', 'responsible_person']

@admin.register(AuditRecord)
class AuditRecordAdmin(SecurityComplianceAdminMixin, admin.ModelAdmin):
    list_display = ['audit_id', 'title', 'audit_type', 'status', 'lead_auditor']
    list_filter = ['audit_type', 'status']
    search_fields = ['audit_id', 'title']
    readonly_fields = ['audit_id']
    filter_horizontal = ['audit_team']
    raw_id_fields = ['lead_auditor']

# ==============================================================================
# 🌐 INFRASTRUCTURE & NETWORK - โครงสร้างพื้นฐานและเครือข่าย
# ==============================================================================
class InfrastructureNetworkAdminMixin:
    """Base admin configuration for infrastructure and network"""
    list_per_page = 20
    save_on_top = True

@admin.register(NetworkDevice)
class NetworkDeviceAdmin(InfrastructureNetworkAdminMixin, admin.ModelAdmin):
    list_display = ['device_name', 'device_type', 'ip_address', 'status', 'last_ping']
    list_filter = ['device_type', 'status', 'last_ping']
    search_fields = ['device_name', 'ip_address', 'mac_address']
    raw_id_fields = ['asset']

@admin.register(IPAddressAllocation)
class IPAddressAllocationAdmin(InfrastructureNetworkAdminMixin, admin.ModelAdmin):
    list_display = ['ip_address', 'subnet', 'status', 'asset', 'hostname']
    list_filter = ['status', 'subnet', 'allocation_date']
    search_fields = ['ip_address', 'hostname']
    raw_id_fields = ['asset', 'allocated_by']

@admin.register(NetworkPort)
class NetworkPortAdmin(InfrastructureNetworkAdminMixin, admin.ModelAdmin):
    list_display = ['device', 'port_number', 'port_type', 'status', 'speed_mbps']
    list_filter = ['device', 'port_type', 'status']
    search_fields = ['device__device_name', 'port_number']
    raw_id_fields = ['device']

@admin.register(NetworkMonitoring)
class NetworkMonitoringAdmin(InfrastructureNetworkAdminMixin, admin.ModelAdmin):
    list_display = ['device', 'metric_type', 'value', 'unit', 'is_alert', 'timestamp']
    list_filter = ['device', 'metric_type', 'is_alert', 'timestamp']
    search_fields = ['device__device_name']
    readonly_fields = ['timestamp']
    raw_id_fields = ['device']

@admin.register(BackupPolicy)
class BackupPolicyAdmin(InfrastructureNetworkAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'backup_type', 'frequency', 'retention_days', 'is_active']
    list_filter = ['backup_type', 'frequency', 'is_active']
    search_fields = ['name']
    filter_horizontal = ['assets']

@admin.register(BackupJob)
class BackupJobAdmin(InfrastructureNetworkAdminMixin, admin.ModelAdmin):
    list_display = ['job_id', 'policy', 'asset', 'status', 'start_time', 'backup_size_gb']
    list_filter = ['policy', 'status', 'start_time']
    search_fields = ['job_id']
    readonly_fields = ['job_id']
    raw_id_fields = ['policy', 'asset']

@admin.register(DisasterRecoveryPlan)
class DisasterRecoveryPlanAdmin(InfrastructureNetworkAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'priority', 'rpo_hours', 'rto_hours', 'is_active']
    list_filter = ['plan_type', 'priority', 'is_active']
    search_fields = ['name']
    filter_horizontal = ['assets']

@admin.register(DisasterRecoveryTest)
class DisasterRecoveryTestAdmin(InfrastructureNetworkAdminMixin, admin.ModelAdmin):
    list_display = ['test_id', 'plan', 'test_type', 'status', 'scheduled_date']
    list_filter = ['plan', 'test_type', 'status']
    search_fields = ['test_id']
    readonly_fields = ['test_id']
    raw_id_fields = ['plan', 'test_coordinator']
    filter_horizontal = ['participants']


@admin.register(InventoryItem)
class InventoryItemAdmin(AssetInventoryAdminMixin, admin.ModelAdmin):
    list_display = ['item_code', 'name', 'item_type', 'vendor', 'quantity_on_hand', 'minimum_stock_level']
    list_filter = ['item_type', 'vendor', 'location']
    search_fields = ['item_code', 'name', 'part_number']
    raw_id_fields = ['vendor', 'location']

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(AssetInventoryAdminMixin, admin.ModelAdmin):
    list_display = ['request_number', 'title', 'requested_by', 'priority', 'status', 'total_amount']
    list_filter = ['priority', 'status', 'needed_by_date']
    search_fields = ['request_number', 'title']
    readonly_fields = ['request_number']
    raw_id_fields = ['requested_by', 'approved_by']

@admin.register(PurchaseRequestItem)
class PurchaseRequestItemAdmin(AssetInventoryAdminMixin, admin.ModelAdmin):
    list_display = ['purchase_request', 'item_description', 'quantity', 'unit_price', 'total_price', 'vendor']
    list_filter = ['purchase_request__status', 'vendor']
    search_fields = ['purchase_request__request_number', 'item_description']
    readonly_fields = ['total_price']
    raw_id_fields = ['purchase_request', 'vendor']

# ==============================================================================
# 📊 MONITORING & ANALYTICS - การติดตามและการวิเคราะห์
# ==============================================================================
class MonitoringAnalyticsAdminMixin:
    """Base admin configuration for monitoring and analytics"""
    list_per_page = 30
    save_on_top = True

@admin.register(SystemMonitoring)
class SystemMonitoringAdmin(MonitoringAnalyticsAdminMixin, admin.ModelAdmin):
    list_display = ['asset', 'metric_type', 'value', 'unit', 'timestamp']
    list_filter = ['asset', 'metric_type', 'timestamp']
    search_fields = ['asset__name', 'metric_type']
    readonly_fields = ['timestamp']
    raw_id_fields = ['asset']

@admin.register(Alert)
class AlertAdmin(MonitoringAnalyticsAdminMixin, admin.ModelAdmin):
    list_display = ['alert_id', 'title', 'severity', 'status', 'asset', 'created_at']
    list_filter = ['severity', 'status', 'created_at']
    search_fields = ['alert_id', 'title']
    readonly_fields = ['alert_id', 'created_at']
    raw_id_fields = ['asset', 'acknowledged_by', 'resolved_by']

@admin.register(AlertRule)
class AlertRuleAdmin(MonitoringAnalyticsAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'metric_type', 'condition', 'threshold_value', 'severity', 'is_active']
    list_filter = ['metric_type', 'condition', 'severity', 'is_active']
    search_fields = ['name']
    filter_horizontal = ['assets']

@admin.register(Report)
class ReportAdmin(MonitoringAnalyticsAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'report_type', 'frequency', 'created_by', 'is_active', 'last_generated']
    list_filter = ['report_type', 'frequency', 'is_active']
    search_fields = ['name']
    readonly_fields = ['last_generated']
    raw_id_fields = ['created_by']

@admin.register(ReportGeneration)
class ReportGenerationAdmin(MonitoringAnalyticsAdminMixin, admin.ModelAdmin):
    list_display = ['report', 'generated_by', 'status', 'file_size_mb', 'created_at']
    list_filter = ['report', 'status', 'created_at']
    search_fields = ['report__name']
    readonly_fields = ['created_at', 'completed_at']
    raw_id_fields = ['report', 'generated_by']

# ==============================================================================
# 📱 MOBILE & DEVICE MANAGEMENT - การจัดการอุปกรณ์มือถือ
# ==============================================================================
class MobileDeviceAdminMixin:
    """Base admin configuration for mobile device management"""
    list_per_page = 25
    save_on_top = True

@admin.register(MobileDevice)
class MobileDeviceAdmin(MobileDeviceAdminMixin, admin.ModelAdmin):
    list_display = ['device_name', 'device_type', 'platform', 'assigned_user', 'status', 'last_seen']
    list_filter = ['device_type', 'platform', 'status', 'is_supervised']
    search_fields = ['device_id', 'device_name', 'serial_number', 'imei']
    readonly_fields = ['storage_available_gb']
    raw_id_fields = ['assigned_user']

@admin.register(MobileAppManagement)  
class MobileAppManagementAdmin(MobileDeviceAdminMixin, admin.ModelAdmin):
    list_display = ['app_name', 'bundle_id', 'version', 'app_type', 'is_active', 'created_by']
    list_filter = ['app_type', 'is_active']
    search_fields = ['app_name', 'bundle_id']
    filter_horizontal = ['target_devices']
    raw_id_fields = ['created_by']

@admin.register(MobileSecurityPolicy)
class MobileSecurityPolicyAdmin(MobileDeviceAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'policy_type', 'enforcement_level', 'is_active', 'created_by']
    list_filter = ['policy_type', 'enforcement_level', 'is_active']
    search_fields = ['name']
    filter_horizontal = ['target_devices']
    raw_id_fields = ['created_by']

# ==============================================================================
# 📚 KNOWLEDGE & TRAINING - ความรู้และการฝึกอบรม
# ==============================================================================
class KnowledgeTrainingAdminMixin:
    """Base admin configuration for knowledge and training"""
    list_per_page = 20
    save_on_top = True

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(KnowledgeTrainingAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'article_type', 'status', 'category', 'author', 'view_count']
    list_filter = ['article_type', 'status', 'category', 'created_at']
    search_fields = ['title', 'content', 'tags']
    readonly_fields = ['view_count', 'helpful_votes', 'not_helpful_votes', 'helpfulness_score']
    filter_horizontal = ['reviewers']
    raw_id_fields = ['author']

@admin.register(TrainingRecord)
class TrainingRecordAdmin(KnowledgeTrainingAdminMixin, admin.ModelAdmin):
    list_display = ['trainee', 'title', 'training_type', 'status', 'scheduled_date', 'score']
    list_filter = ['training_type', 'status', 'certificate_issued', 'scheduled_date']
    search_fields = ['title', 'trainee__username']
    raw_id_fields = ['trainee', 'trainer']


