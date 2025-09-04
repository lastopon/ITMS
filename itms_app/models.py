from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Asset(models.Model):
    ASSET_STATUS_CHOICES = [
        ('active', '🟢 Active'),
        ('inactive', '🔴 Inactive'),
        ('maintenance', '🔧 Under Maintenance'),
        ('retired', '📦 Retired'),
        ('disposed', '🗑️ Disposed'),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', '⭐ Excellent'),
        ('good', '✅ Good'),
        ('fair', '⚠️ Fair'),
        ('poor', '❌ Poor'),
        ('unknown', '❓ Unknown'),
    ]
    
    # Basic Information
    asset_tag = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Unique identifier for this asset (e.g., ITMS-2024-001)"
    )
    name = models.CharField(
        max_length=200,
        help_text="Asset name or description"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the asset"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        help_text="Asset category"
    )
    
    # Hardware Details
    serial_number = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Manufacturer's serial number"
    )
    model = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Model name/number"
    )
    manufacturer = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Manufacturer or brand"
    )
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='unknown',
        help_text="Physical condition of the asset"
    )
    
    # Financial Information
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Supplier or vendor"
    )
    purchase_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Date when asset was purchased"
    )
    purchase_cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Original purchase cost"
    )
    warranty_expiry = models.DateField(
        null=True, 
        blank=True,
        help_text="Warranty expiration date"
    )
    depreciation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual depreciation rate (%)"
    )
    
    # Location and Assignment
    location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE,
        help_text="Physical location of the asset"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Person responsible for this asset"
    )
    status = models.CharField(
        max_length=20, 
        choices=ASSET_STATUS_CHOICES, 
        default='active',
        help_text="Current operational status"
    )
    
    # Additional Information
    barcode = models.CharField(
        max_length=100,
        blank=True,
        help_text="Barcode number if applicable"
    )
    asset_image = models.ImageField(
        upload_to='assets/',
        blank=True,
        null=True,
        help_text="Photo of the asset"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes and comments"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset_tag} - {self.name}"

    class Meta:
        ordering = ['-created_at']


class MaintenanceRecord(models.Model):
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('emergency', 'Emergency'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    maintenance_date = models.DateTimeField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset} - {self.maintenance_type} on {self.maintenance_date.date()}"

    class Meta:
        ordering = ['-maintenance_date']


class SoftwareLicense(models.Model):
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=50, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    license_key = models.CharField(max_length=500, blank=True)
    license_type = models.CharField(max_length=100)  # Per user, Per device, Site license, etc.
    purchase_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    max_installations = models.IntegerField()
    current_installations = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.version}"

    @property
    def available_installations(self):
        return self.max_installations - self.current_installations

    class Meta:
        ordering = ['-created_at']


class SoftwareInstallation(models.Model):
    software_license = models.ForeignKey(SoftwareLicense, on_delete=models.CASCADE, related_name='installations')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='software_installations')
    installed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    installation_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.software_license} on {self.asset}"

    class Meta:
        unique_together = ['software_license', 'asset']
        ordering = ['-installation_date']


class HelpDeskTicket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    ticket_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_tickets')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import random
            base_number = f"TK{timezone.now().strftime('%Y%m%d%H%M%S')}"
            # Add random suffix to ensure uniqueness
            counter = 0
            ticket_number = base_number
            while HelpDeskTicket.objects.filter(ticket_number=ticket_number).exists():
                counter += 1
                ticket_number = f"{base_number}{counter:03d}"
                if counter > 999:  # Safety break
                    ticket_number = f"TK{timezone.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000,9999)}"
                    break
            self.ticket_number = ticket_number
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number} - {self.title}"

    class Meta:
        ordering = ['-created_at']


class Reservation(models.Model):
    RESERVATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    RESERVATION_TYPE_CHOICES = [
        ('meeting_room', 'Meeting Room'),
        ('vehicle', 'Vehicle'),
        ('equipment', 'Equipment'),
        ('other', 'Other'),
    ]

    reservation_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='reservations')
    reserved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reservations')
    reservation_type = models.CharField(max_length=20, choices=RESERVATION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=RESERVATION_STATUS_CHOICES, default='pending')
    
    # Reservation timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    # Additional details
    number_of_people = models.IntegerField(null=True, blank=True, help_text="For meeting rooms or vehicles")
    purpose = models.CharField(max_length=300, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    special_requirements = models.TextField(blank=True)
    
    # Approval and notes
    approval_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reservation_number:
            import random
            base_number = f"RSV{timezone.now().strftime('%Y%m%d%H%M%S')}"
            counter = 0
            reservation_number = base_number
            while Reservation.objects.filter(reservation_number=reservation_number).exists():
                counter += 1
                reservation_number = f"{base_number}{counter:03d}"
                if counter > 999:  # Safety break
                    reservation_number = f"RSV{timezone.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000,9999)}"
                    break
            self.reservation_number = reservation_number
        
        if self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reservation_number} - {self.title} ({self.asset.name})"

    @property
    def duration_hours(self):
        """Calculate reservation duration in hours"""
        delta = self.end_datetime - self.start_datetime
        return round(delta.total_seconds() / 3600, 2)

    @property
    def is_active(self):
        """Check if reservation is currently active"""
        now = timezone.now()
        return self.status == 'approved' and self.start_datetime <= now <= self.end_datetime

    @property
    def is_upcoming(self):
        """Check if reservation is upcoming"""
        now = timezone.now()
        return self.status == 'approved' and self.start_datetime > now

    def can_be_cancelled(self):
        """Check if reservation can be cancelled"""
        now = timezone.now()
        return self.status in ['pending', 'approved'] and self.start_datetime > now

    def get_status_color(self):
        """Get CSS color class for status display"""
        color_map = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'active': 'info',
            'completed': 'secondary',
            'cancelled': 'dark',
        }
        return color_map.get(self.status, 'secondary')

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_datetime__gt=models.F('start_datetime')),
                name='end_datetime_after_start_datetime'
            )
        ]


# ===============================
# 1. SECURITY MANAGEMENT SYSTEM
# ===============================

class SecurityIncident(models.Model):
    INCIDENT_TYPE_CHOICES = [
        ('data_breach', 'Data Breach'),
        ('malware', 'Malware Attack'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('phishing', 'Phishing Attack'),
        ('ddos', 'DDoS Attack'),
        ('insider_threat', 'Insider Threat'),
        ('physical_security', 'Physical Security'),
        ('social_engineering', 'Social Engineering'),
        ('other', 'Other'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('investigating', 'Investigating'),
        ('contained', 'Contained'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    incident_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    affected_assets = models.ManyToManyField(Asset, blank=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_incidents')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    discovered_date = models.DateTimeField()
    resolution_date = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.incident_id:
            base_id = f"SEC{timezone.now().strftime('%Y%m%d%H%M%S')}"
            self.incident_id = base_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.incident_id} - {self.title}"

    class Meta:
        ordering = ['-created_at']


class VulnerabilityAssessment(models.Model):
    RISK_LEVEL_CHOICES = [
        ('info', 'Informational'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('fixed', 'Fixed'),
        ('mitigated', 'Mitigated'),
        ('accepted', 'Accepted Risk'),
    ]

    vulnerability_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    cve_id = models.CharField(max_length=20, blank=True, help_text="Common Vulnerabilities and Exposures ID")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified')
    affected_assets = models.ManyToManyField(Asset, blank=True)
    discovery_method = models.CharField(max_length=100, blank=True)
    discovered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_vulnerabilities')
    discovery_date = models.DateTimeField()
    target_fix_date = models.DateField(null=True, blank=True)
    fix_date = models.DateTimeField(null=True, blank=True)
    remediation_notes = models.TextField(blank=True)
    verification_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.vulnerability_id:
            base_id = f"VUL{timezone.now().strftime('%Y%m%d%H%M%S')}"
            self.vulnerability_id = base_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vulnerability_id} - {self.title}"

    class Meta:
        ordering = ['-created_at']


class AccessControlMatrix(models.Model):
    ACCESS_TYPE_CHOICES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('execute', 'Execute'),
        ('admin', 'Admin'),
        ('full_control', 'Full Control'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES)
    granted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='granted_access')
    granted_date = models.DateTimeField()
    expiry_date = models.DateTimeField(null=True, blank=True)
    justification = models.TextField()
    is_active = models.BooleanField(default=True)
    revoked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='revoked_access')
    revoked_date = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.asset} ({self.access_type})"

    class Meta:
        unique_together = ['user', 'asset', 'access_type']
        ordering = ['-created_at']


class SecurityAuditLog(models.Model):
    EVENT_TYPE_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('access_granted', 'Access Granted'),
        ('access_denied', 'Access Denied'),
        ('data_access', 'Data Access'),
        ('configuration_change', 'Configuration Change'),
        ('system_event', 'System Event'),
        ('security_event', 'Security Event'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    event_description = models.TextField()
    outcome = models.CharField(max_length=20, choices=[('success', 'Success'), ('failure', 'Failure')])
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='low')
    additional_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.timestamp} - {self.event_type} - {self.user}"

    class Meta:
        ordering = ['-timestamp']


# ===============================
# 2. NETWORK MANAGEMENT SYSTEM
# ===============================

class NetworkDevice(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('router', 'Router'),
        ('switch', 'Switch'),
        ('firewall', 'Firewall'),
        ('access_point', 'Access Point'),
        ('load_balancer', 'Load Balancer'),
        ('proxy', 'Proxy Server'),
        ('vpn_gateway', 'VPN Gateway'),
        ('modem', 'Modem'),
        ('bridge', 'Bridge'),
        ('hub', 'Hub'),
    ]

    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('maintenance', 'Under Maintenance'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    device_name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='network_device')
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17, blank=True)
    subnet_mask = models.GenericIPAddressField(null=True, blank=True)
    default_gateway = models.GenericIPAddressField(null=True, blank=True)
    dns_servers = models.TextField(blank=True, help_text="Comma-separated DNS servers")
    vlan_id = models.IntegerField(null=True, blank=True)
    port_count = models.IntegerField(null=True, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    management_url = models.URLField(blank=True)
    snmp_community = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    last_ping = models.DateTimeField(null=True, blank=True)
    uptime_hours = models.FloatField(null=True, blank=True)
    configuration_backup = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device_name} ({self.ip_address})"

    class Meta:
        ordering = ['device_name']


class IPAddressAllocation(models.Model):
    STATUS_CHOICES = [
        ('allocated', 'Allocated'),
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('blocked', 'Blocked'),
    ]

    ip_address = models.GenericIPAddressField(unique=True)
    subnet = models.CharField(max_length=18, help_text="CIDR notation (e.g., 192.168.1.0/24)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    hostname = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    allocated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    allocation_date = models.DateTimeField(null=True, blank=True)
    lease_expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ip_address} - {self.status}"

    class Meta:
        ordering = ['ip_address']


class NetworkPort(models.Model):
    PORT_TYPE_CHOICES = [
        ('ethernet', 'Ethernet'),
        ('fiber', 'Fiber Optic'),
        ('console', 'Console'),
        ('management', 'Management'),
        ('uplink', 'Uplink'),
        ('trunk', 'Trunk'),
        ('access', 'Access'),
    ]

    STATUS_CHOICES = [
        ('up', 'Up'),
        ('down', 'Down'),
        ('disabled', 'Disabled'),
        ('error', 'Error'),
    ]

    device = models.ForeignKey(NetworkDevice, on_delete=models.CASCADE, related_name='ports')
    port_number = models.CharField(max_length=20)
    port_type = models.CharField(max_length=20, choices=PORT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='down')
    description = models.CharField(max_length=200, blank=True)
    connected_to = models.CharField(max_length=200, blank=True, help_text="Description of what is connected")
    vlan_id = models.IntegerField(null=True, blank=True)
    speed_mbps = models.IntegerField(null=True, blank=True)
    duplex = models.CharField(max_length=10, choices=[('half', 'Half'), ('full', 'Full')], blank=True)
    is_monitored = models.BooleanField(default=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device.device_name} - Port {self.port_number}"

    class Meta:
        unique_together = ['device', 'port_number']
        ordering = ['device', 'port_number']


class NetworkMonitoring(models.Model):
    METRIC_TYPE_CHOICES = [
        ('ping', 'Ping Response'),
        ('bandwidth', 'Bandwidth Usage'),
        ('cpu', 'CPU Usage'),
        ('memory', 'Memory Usage'),
        ('temperature', 'Temperature'),
        ('port_status', 'Port Status'),
        ('traffic', 'Network Traffic'),
    ]

    device = models.ForeignKey(NetworkDevice, on_delete=models.CASCADE, related_name='monitoring_data')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    threshold_min = models.FloatField(null=True, blank=True)
    threshold_max = models.FloatField(null=True, blank=True)
    is_alert = models.BooleanField(default=False)
    additional_data = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device} - {self.metric_type}: {self.value}"

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'metric_type', 'timestamp']),
        ]


# =======================================
# 3. BACKUP & DISASTER RECOVERY SYSTEM
# =======================================

class BackupPolicy(models.Model):
    FREQUENCY_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    BACKUP_TYPE_CHOICES = [
        ('full', 'Full Backup'),
        ('incremental', 'Incremental Backup'),
        ('differential', 'Differential Backup'),
        ('snapshot', 'Snapshot'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPE_CHOICES)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    retention_days = models.IntegerField(help_text="Number of days to retain backups")
    assets = models.ManyToManyField(Asset, blank=True)
    backup_location = models.TextField(help_text="Storage location/path for backups")
    is_active = models.BooleanField(default=True)
    next_scheduled = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.frequency})"

    class Meta:
        ordering = ['name']


class BackupJob(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    job_id = models.CharField(max_length=20, unique=True)
    policy = models.ForeignKey(BackupPolicy, on_delete=models.CASCADE, related_name='backup_jobs')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    backup_size_gb = models.FloatField(null=True, blank=True)
    backup_location = models.TextField(blank=True)
    success_message = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    verification_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('failed', 'Verification Failed'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.job_id:
            base_id = f"BK{timezone.now().strftime('%Y%m%d%H%M%S')}"
            self.job_id = base_id
        super().save(*args, **kwargs)

    @property
    def duration_minutes(self):
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return round(delta.total_seconds() / 60, 2)
        return None

    def __str__(self):
        return f"{self.job_id} - {self.asset} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class DisasterRecoveryPlan(models.Model):
    PLAN_TYPE_CHOICES = [
        ('hot_site', 'Hot Site'),
        ('warm_site', 'Warm Site'),
        ('cold_site', 'Cold Site'),
        ('cloud_based', 'Cloud-based'),
        ('mobile_site', 'Mobile Site'),
    ]

    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    assets = models.ManyToManyField(Asset, blank=True)
    rpo_hours = models.FloatField(help_text="Recovery Point Objective in hours")
    rto_hours = models.FloatField(help_text="Recovery Time Objective in hours")
    recovery_steps = models.TextField(help_text="Detailed recovery procedures")
    contact_list = models.TextField(help_text="Emergency contact information")
    testing_frequency = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annually', 'Semi-annually'),
        ('annually', 'Annually'),
    ])
    last_tested = models.DateTimeField(null=True, blank=True)
    next_test_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.plan_type})"

    class Meta:
        ordering = ['priority', 'name']


class DisasterRecoveryTest(models.Model):
    TEST_TYPE_CHOICES = [
        ('tabletop', 'Tabletop Exercise'),
        ('walkthrough', 'Walkthrough Test'),
        ('simulation', 'Simulation Test'),
        ('parallel', 'Parallel Test'),
        ('full_interruption', 'Full Interruption Test'),
    ]

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    test_id = models.CharField(max_length=20, unique=True)
    plan = models.ForeignKey(DisasterRecoveryPlan, on_delete=models.CASCADE, related_name='tests')
    test_type = models.CharField(max_length=30, choices=TEST_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    scheduled_date = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    test_coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='dr_tests', blank=True)
    objectives = models.TextField()
    results = models.TextField(blank=True)
    issues_identified = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    success_criteria_met = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.test_id:
            base_id = f"DR{timezone.now().strftime('%Y%m%d%H%M%S')}"
            self.test_id = base_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.test_id} - {self.plan.name} ({self.test_type})"

    class Meta:
        ordering = ['-scheduled_date']


# ===================================
# 4. INVENTORY & PROCUREMENT SYSTEM
# ===================================

class InventoryItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('component', 'Component'),
        ('consumable', 'Consumable'),
        ('spare_part', 'Spare Part'),
        ('tool', 'Tool'),
        ('cable', 'Cable'),
        ('accessory', 'Accessory'),
    ]

    item_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    part_number = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    quantity_on_hand = models.IntegerField(default=0)
    minimum_stock_level = models.IntegerField(default=0)
    maximum_stock_level = models.IntegerField(null=True, blank=True)
    reorder_point = models.IntegerField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    storage_location = models.CharField(max_length=100, blank=True, help_text="Specific storage location within the location")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item_code} - {self.name}"

    @property
    def total_value(self):
        return self.quantity_on_hand * self.unit_price

    @property
    def needs_reorder(self):
        return self.quantity_on_hand <= (self.reorder_point or self.minimum_stock_level)

    class Meta:
        ordering = ['item_code']


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    request_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchase_requests')
    department = models.CharField(max_length=100, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_purchases')
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    budget_code = models.CharField(max_length=50, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    needed_by_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.request_number:
            base_number = f"PR{timezone.now().strftime('%Y%m%d%H%M%S')}"
            self.request_number = base_number
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_number} - {self.title}"

    class Meta:
        ordering = ['-created_at']


class PurchaseRequestItem(models.Model):
    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='items')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, null=True, blank=True)
    item_description = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.purchase_request.request_number} - {self.item_description}"


# ===================================
# 5. MONITORING & ALERTING SYSTEM
# ===================================

class SystemMonitoring(models.Model):
    METRIC_TYPE_CHOICES = [
        ('cpu', 'CPU Usage'),
        ('memory', 'Memory Usage'),
        ('disk', 'Disk Usage'),
        ('network', 'Network Usage'),
        ('temperature', 'Temperature'),
        ('power', 'Power Consumption'),
        ('uptime', 'System Uptime'),
        ('response_time', 'Response Time'),
        ('throughput', 'Throughput'),
        ('error_rate', 'Error Rate'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='monitoring_metrics')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.asset} - {self.metric_type}: {self.value} {self.unit}"

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['asset', 'metric_type', 'timestamp']),
        ]


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    alert_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='alerts')
    metric_type = models.CharField(max_length=20, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    actual_value = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.alert_id:
            base_id = f"AL{timezone.now().strftime('%Y%m%d%H%M%S')}"
            self.alert_id = base_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.alert_id} - {self.title} ({self.severity})"

    class Meta:
        ordering = ['-created_at']


class AlertRule(models.Model):
    CONDITION_CHOICES = [
        ('greater_than', 'Greater Than'),
        ('less_than', 'Less Than'),
        ('equals', 'Equals'),
        ('not_equals', 'Not Equals'),
        ('contains', 'Contains'),
        ('not_responding', 'Not Responding'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    metric_type = models.CharField(max_length=20)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    threshold_value = models.FloatField()
    severity = models.CharField(max_length=20, choices=Alert.SEVERITY_CHOICES)
    assets = models.ManyToManyField(Asset, blank=True)
    is_active = models.BooleanField(default=True)
    notification_emails = models.TextField(blank=True, help_text="Comma-separated email addresses")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.metric_type} {self.condition} {self.threshold_value})"

    class Meta:
        ordering = ['name']


# ===================================
# 6. KNOWLEDGE MANAGEMENT SYSTEM
# ===================================

class KnowledgeBase(models.Model):
    ARTICLE_TYPE_CHOICES = [
        ('troubleshooting', 'Troubleshooting Guide'),
        ('how_to', 'How-to Guide'),
        ('faq', 'Frequently Asked Questions'),
        ('best_practice', 'Best Practices'),
        ('policy', 'Policy Document'),
        ('procedure', 'Standard Procedure'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    article_type = models.CharField(max_length=20, choices=ARTICLE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_articles')
    reviewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='reviewed_articles', blank=True)
    view_count = models.IntegerField(default=0)
    helpful_votes = models.IntegerField(default=0)
    not_helpful_votes = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def helpfulness_score(self):
        total_votes = self.helpful_votes + self.not_helpful_votes
        if total_votes == 0:
            return 0
        return round((self.helpful_votes / total_votes) * 100, 1)

    class Meta:
        ordering = ['-updated_at']


class TrainingRecord(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]

    TRAINING_TYPE_CHOICES = [
        ('orientation', 'New Employee Orientation'),
        ('technical', 'Technical Training'),
        ('security', 'Security Training'),
        ('compliance', 'Compliance Training'),
        ('certification', 'Certification Program'),
        ('refresher', 'Refresher Training'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    training_type = models.CharField(max_length=20, choices=TRAINING_TYPE_CHOICES)
    trainee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='training_records')
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conducted_trainings')
    scheduled_date = models.DateTimeField()
    completion_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    score = models.FloatField(null=True, blank=True, help_text="Training score (0-100)")
    certificate_issued = models.BooleanField(default=False)
    certificate_expiry = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trainee} - {self.title}"

    class Meta:
        ordering = ['-scheduled_date']


# ===================================
# 7. COMPLIANCE & AUDIT SYSTEM
# ===================================

class ComplianceFramework(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., ISO 27001, GDPR, SOX")
    description = models.TextField()
    version = models.CharField(max_length=20, blank=True)
    effective_date = models.DateField()
    review_frequency_months = models.IntegerField(default=12)
    next_review_date = models.DateField()
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.version}"

    class Meta:
        ordering = ['name']


class ComplianceRequirement(models.Model):
    COMPLIANCE_STATUS_CHOICES = [
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partially_compliant', 'Partially Compliant'),
        ('not_assessed', 'Not Assessed'),
    ]

    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE, related_name='requirements')
    control_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField()
    implementation_guidance = models.TextField(blank=True)
    evidence_required = models.TextField(blank=True)
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=COMPLIANCE_STATUS_CHOICES, default='not_assessed')
    last_assessed = models.DateTimeField(null=True, blank=True)
    next_assessment = models.DateField(null=True, blank=True)
    assessment_notes = models.TextField(blank=True)
    remediation_plan = models.TextField(blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.framework.name} - {self.control_id}: {self.title}"

    class Meta:
        ordering = ['framework', 'control_id']
        unique_together = ['framework', 'control_id']


class AuditRecord(models.Model):
    AUDIT_TYPE_CHOICES = [
        ('internal', 'Internal Audit'),
        ('external', 'External Audit'),
        ('compliance', 'Compliance Audit'),
        ('security', 'Security Audit'),
        ('financial', 'Financial Audit'),
        ('operational', 'Operational Audit'),
    ]

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    audit_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    audit_type = models.CharField(max_length=20, choices=AUDIT_TYPE_CHOICES)
    scope = models.TextField()
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.SET_NULL, null=True, blank=True)
    lead_auditor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='led_audits')
    audit_team = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='audit_participations', blank=True)
    planned_start_date = models.DateField()
    planned_end_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    findings_summary = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    management_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.audit_id:
            base_id = f"AUD{timezone.now().strftime('%Y%m%d%H%M%S')}"
            self.audit_id = base_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.audit_id} - {self.title}"

    class Meta:
        ordering = ['-planned_start_date']


# ==========================================
# 8. ADVANCED REPORTING & ANALYTICS SYSTEM
# ==========================================

class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('asset_utilization', 'Asset Utilization'),
        ('cost_analysis', 'Cost Analysis'),
        ('performance_metrics', 'Performance Metrics'),
        ('security_summary', 'Security Summary'),
        ('compliance_status', 'Compliance Status'),
        ('maintenance_summary', 'Maintenance Summary'),
        ('inventory_report', 'Inventory Report'),
        ('custom', 'Custom Report'),
    ]

    FREQUENCY_CHOICES = [
        ('on_demand', 'On Demand'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='on_demand')
    parameters = models.JSONField(blank=True, null=True, help_text="Report parameters and filters")
    recipients = models.TextField(blank=True, help_text="Comma-separated email addresses")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    next_generation = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ReportGeneration(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='generations')
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    file_path = models.CharField(max_length=500, blank=True)
    file_size_mb = models.FloatField(null=True, blank=True)
    generation_time_seconds = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    parameters_used = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.report.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']


# ===================================
# 9. MOBILE DEVICE MANAGEMENT SYSTEM
# ===================================

class MobileDevice(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('smartphone', 'Smartphone'),
        ('tablet', 'Tablet'),
        ('laptop', 'Laptop'),
        ('wearable', 'Wearable Device'),
    ]

    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('windows', 'Windows'),
        ('macos', 'macOS'),
    ]

    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('lost', 'Lost'),
        ('stolen', 'Stolen'),
        ('retired', 'Retired'),
        ('wiped', 'Wiped'),
    ]

    device_id = models.CharField(max_length=100, unique=True)
    device_name = models.CharField(max_length=200)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    os_version = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    imei = models.CharField(max_length=20, blank=True, help_text="International Mobile Equipment Identity")
    phone_number = models.CharField(max_length=20, blank=True)
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='mobile_devices')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    is_supervised = models.BooleanField(default=False)
    is_encrypted = models.BooleanField(default=False)
    passcode_enabled = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    location_latitude = models.FloatField(null=True, blank=True)
    location_longitude = models.FloatField(null=True, blank=True)
    location_accuracy = models.FloatField(null=True, blank=True)
    battery_level = models.IntegerField(null=True, blank=True)
    storage_total_gb = models.FloatField(null=True, blank=True)
    storage_used_gb = models.FloatField(null=True, blank=True)
    enrollment_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device_name} ({self.device_id})"

    @property
    def storage_available_gb(self):
        if self.storage_total_gb and self.storage_used_gb:
            return self.storage_total_gb - self.storage_used_gb
        return None

    class Meta:
        ordering = ['device_name']


class MobileAppManagement(models.Model):
    APP_TYPE_CHOICES = [
        ('mandatory', 'Mandatory'),
        ('optional', 'Optional'),
        ('blacklisted', 'Blacklisted'),
    ]

    app_name = models.CharField(max_length=200)
    bundle_id = models.CharField(max_length=200, help_text="App bundle identifier")
    version = models.CharField(max_length=50, blank=True)
    app_type = models.CharField(max_length=20, choices=APP_TYPE_CHOICES)
    description = models.TextField(blank=True)
    target_devices = models.ManyToManyField(MobileDevice, blank=True)
    is_active = models.BooleanField(default=True)
    install_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.app_name} ({self.app_type})"

    class Meta:
        ordering = ['app_name']


class MobileSecurityPolicy(models.Model):
    POLICY_TYPE_CHOICES = [
        ('device_restrictions', 'Device Restrictions'),
        ('app_restrictions', 'App Restrictions'),
        ('network_access', 'Network Access'),
        ('data_protection', 'Data Protection'),
        ('compliance', 'Compliance Policy'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    policy_type = models.CharField(max_length=30, choices=POLICY_TYPE_CHOICES)
    policy_rules = models.JSONField(help_text="Policy rules and configurations")
    target_devices = models.ManyToManyField(MobileDevice, blank=True)
    is_active = models.BooleanField(default=True)
    enforcement_level = models.CharField(max_length=20, choices=[
        ('warn', 'Warning Only'),
        ('enforce', 'Enforce Policy'),
        ('block', 'Block Access'),
    ], default='enforce')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# ===================================
# 10. SERVICE CATALOG & ITSM SYSTEM
# ===================================

class ServiceCatalog(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('hardware', 'Hardware Service'),
        ('software', 'Software Service'),
        ('network', 'Network Service'),
        ('security', 'Security Service'),
        ('support', 'Support Service'),
        ('cloud', 'Cloud Service'),
        ('consulting', 'Consulting Service'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('development', 'Under Development'),
        ('retired', 'Retired'),
    ]

    service_name = models.CharField(max_length=200)
    service_code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    service_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_services')
    business_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_owned_services')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='development')
    cost_per_user = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sla_target = models.CharField(max_length=100, blank=True, help_text="Service Level Agreement target")
    dependencies = models.ManyToManyField('self', blank=True, symmetrical=False)
    documentation_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service_code} - {self.service_name}"

    class Meta:
        ordering = ['service_code']


class ServiceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    request_number = models.CharField(max_length=20, unique=True)
    service = models.ForeignKey(ServiceCatalog, on_delete=models.CASCADE, related_name='requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    requested_for = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_services')
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    business_justification = models.TextField(blank=True)
    expected_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_service_requests')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_service_requests')
    approval_date = models.DateTimeField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    work_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.request_number:
            base_number = f"SR{timezone.now().strftime('%Y%m%d%H%M%S')}"
            self.request_number = base_number
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_number} - {self.title}"

    class Meta:
        ordering = ['-created_at']


class ChangeManagement(models.Model):
    CHANGE_TYPE_CHOICES = [
        ('standard', 'Standard Change'),
        ('normal', 'Normal Change'),
        ('emergency', 'Emergency Change'),
    ]

    RISK_LEVEL_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('implemented', 'Implemented'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]

    change_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_changes')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_changes')
    business_justification = models.TextField()
    impact_assessment = models.TextField()
    rollback_plan = models.TextField()
    affected_services = models.ManyToManyField(ServiceCatalog, blank=True)
    affected_assets = models.ManyToManyField(Asset, blank=True)
    planned_start = models.DateTimeField()
    planned_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_changes')
    approval_date = models.DateTimeField(null=True, blank=True)
    implementation_notes = models.TextField(blank=True)
    post_implementation_review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.change_number:
            base_number = f"CH{timezone.now().strftime('%Y%m%d%H%M%S')}"
            self.change_number = base_number
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.change_number} - {self.title}"

    class Meta:
        ordering = ['-created_at']