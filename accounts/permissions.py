# Custom Permissions for ITMS
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ITMSPermissionMixin:
    """
    Mixin class สำหรับจัดการ permissions ขั้นสูง
    ใช้กับ models ที่ต้องการ object-level permissions
    """
    
    class Meta:
        abstract = True
        permissions = [
            ("can_approve", "Can approve requests"),
            ("can_reject", "Can reject requests"),
            ("can_view_all", "Can view all records"),
            ("can_export", "Can export data"),
            ("can_import", "Can import data"),
            ("can_generate_reports", "Can generate reports"),
            ("can_manage_settings", "Can manage system settings"),
        ]


class ITMSPermissionManager:
    """
    Manager class สำหรับจัดการ Groups และ Permissions
    """
    
    # กำหนด Permission Groups ตาม PostgreSQL Role-based approach
    PERMISSION_GROUPS = {
        'IT_Administrators': {
            'description': 'ผู้ดูแลระบบ IT - มีสิทธิ์ทุกอย่าง',
            'color': '#ef4444',  # Red
            'permissions': [
                # User Management
                'auth.add_user', 'auth.change_user', 'auth.delete_user', 'auth.view_user',
                'auth.add_group', 'auth.change_group', 'auth.delete_group', 'auth.view_group',
                
                # All ITMS Models - Full Access
                'itms_app.add_*', 'itms_app.change_*', 'itms_app.delete_*', 'itms_app.view_*',
                'accounts.add_*', 'accounts.change_*', 'accounts.delete_*', 'accounts.view_*',
                
                # Custom Permissions
                'itms_app.can_approve', 'itms_app.can_reject', 'itms_app.can_view_all',
                'itms_app.can_export', 'itms_app.can_import', 'itms_app.can_generate_reports',
                'itms_app.can_manage_settings'
            ]
        },
        
        'Asset_Managers': {
            'description': 'ผู้จัดการทรัพยากร - จัดการทรัพย์สินและซอฟต์แวร์',
            'color': '#3b82f6',  # Blue
            'permissions': [
                # Asset Management
                'itms_app.add_asset', 'itms_app.change_asset', 'itms_app.view_asset',
                'itms_app.add_category', 'itms_app.change_category', 'itms_app.view_category',
                'itms_app.add_location', 'itms_app.change_location', 'itms_app.view_location',
                'itms_app.add_vendor', 'itms_app.change_vendor', 'itms_app.view_vendor',
                
                # Software Management
                'itms_app.add_softwarelicense', 'itms_app.change_softwarelicense', 'itms_app.view_softwarelicense',
                'itms_app.add_softwareinstallation', 'itms_app.change_softwareinstallation', 'itms_app.view_softwareinstallation',
                
                # Maintenance
                'itms_app.add_maintenancerecord', 'itms_app.change_maintenancerecord', 'itms_app.view_maintenancerecord',
                
                # Custom Permissions
                'itms_app.can_export', 'itms_app.can_generate_reports'
            ]
        },
        
        'Security_Officers': {
            'description': 'เจ้าหน้าที่ความปลอดภัย - จัดการด้านความปลอดภัย',
            'color': '#dc2626',  # Dark Red
            'permissions': [
                # Security Management
                'itms_app.add_securityincident', 'itms_app.change_securityincident', 'itms_app.view_securityincident',
                'itms_app.add_vulnerabilityassessment', 'itms_app.change_vulnerabilityassessment', 'itms_app.view_vulnerabilityassessment',
                'itms_app.add_accesscontrolmatrix', 'itms_app.change_accesscontrolmatrix', 'itms_app.view_accesscontrolmatrix',
                'itms_app.add_securityauditlog', 'itms_app.change_securityauditlog', 'itms_app.view_securityauditlog',
                
                # Compliance & Audit
                'itms_app.add_complianceframework', 'itms_app.change_complianceframework', 'itms_app.view_complianceframework',
                'itms_app.add_compliancerequirement', 'itms_app.change_compliancerequirement', 'itms_app.view_compliancerequirement',
                'itms_app.add_auditrecord', 'itms_app.change_auditrecord', 'itms_app.view_auditrecord',
                
                # View Assets (for security assessment)
                'itms_app.view_asset', 'itms_app.view_networkdevice',
                
                # Custom Permissions
                'itms_app.can_view_all', 'itms_app.can_export', 'itms_app.can_generate_reports'
            ]
        },
        
        'Network_Engineers': {
            'description': 'วิศวกรเครือข่าย - จัดการระบบเครือข่าย',
            'color': '#059669',  # Green
            'permissions': [
                # Network Management
                'itms_app.add_networkdevice', 'itms_app.change_networkdevice', 'itms_app.view_networkdevice',
                'itms_app.add_ipaddressallocation', 'itms_app.change_ipaddressallocation', 'itms_app.view_ipaddressallocation',
                'itms_app.add_networkport', 'itms_app.change_networkport', 'itms_app.view_networkport',
                'itms_app.add_networkmonitoring', 'itms_app.change_networkmonitoring', 'itms_app.view_networkmonitoring',
                
                # Monitoring & Alerting
                'itms_app.add_systemmonitoring', 'itms_app.change_systemmonitoring', 'itms_app.view_systemmonitoring',
                'itms_app.add_alert', 'itms_app.change_alert', 'itms_app.view_alert',
                'itms_app.add_alertrule', 'itms_app.change_alertrule', 'itms_app.view_alertrule',
                
                # View Assets (for network planning)
                'itms_app.view_asset', 'itms_app.view_location',
                
                # Custom Permissions
                'itms_app.can_export', 'itms_app.can_generate_reports'
            ]
        },
        
        'Helpdesk_Staff': {
            'description': 'พนักงาน Help Desk - จัดการ tickets และ reservations',
            'color': '#7c3aed',  # Purple
            'permissions': [
                # Help Desk Management
                'itms_app.add_helpdeskticket', 'itms_app.change_helpdeskticket', 'itms_app.view_helpdeskticket',
                'itms_app.add_reservation', 'itms_app.change_reservation', 'itms_app.view_reservation',
                
                # View Assets (for support)
                'itms_app.view_asset', 'itms_app.view_category', 'itms_app.view_location',
                'itms_app.view_softwarelicense', 'itms_app.view_softwareinstallation',
                
                # Knowledge Base
                'itms_app.add_knowledgebase', 'itms_app.change_knowledgebase', 'itms_app.view_knowledgebase',
                'itms_app.add_trainingrecord', 'itms_app.change_trainingrecord', 'itms_app.view_trainingrecord',
                
                # View Users (for ticket assignment)
                'auth.view_user',
                
                # Custom Permissions
                'itms_app.can_approve', 'itms_app.can_reject'  # For reservations
            ]
        },
        
        'Service_Managers': {
            'description': 'ผู้จัดการบริการ - จัดการ Service Catalog และ ITSM',
            'color': '#0891b2',  # Cyan
            'permissions': [
                # Service Catalog & ITSM
                'itms_app.add_servicecatalog', 'itms_app.change_servicecatalog', 'itms_app.view_servicecatalog',
                'itms_app.add_servicerequest', 'itms_app.change_servicerequest', 'itms_app.view_servicerequest',
                'itms_app.add_changemanagement', 'itms_app.change_changemanagement', 'itms_app.view_changemanagement',
                
                # Procurement
                'itms_app.add_inventoryitem', 'itms_app.change_inventoryitem', 'itms_app.view_inventoryitem',
                'itms_app.add_purchaserequest', 'itms_app.change_purchaserequest', 'itms_app.view_purchaserequest',
                'itms_app.add_purchaserequestitem', 'itms_app.change_purchaserequestitem', 'itms_app.view_purchaserequestitem',
                
                # View related data
                'itms_app.view_asset', 'itms_app.view_vendor', 'itms_app.view_category',
                
                # Custom Permissions
                'itms_app.can_approve', 'itms_app.can_reject', 'itms_app.can_generate_reports'
            ]
        },
        
        'Backup_Operators': {
            'description': 'ผู้ดำเนินการสำรองข้อมูล - จัดการ Backup และ DR',
            'color': '#ea580c',  # Orange
            'permissions': [
                # Backup & DR Management
                'itms_app.add_backuppolicy', 'itms_app.change_backuppolicy', 'itms_app.view_backuppolicy',
                'itms_app.add_backupjob', 'itms_app.change_backupjob', 'itms_app.view_backupjob',
                'itms_app.add_disasterrecoveryplan', 'itms_app.change_disasterrecoveryplan', 'itms_app.view_disasterrecoveryplan',
                'itms_app.add_disasterrecoverytest', 'itms_app.change_disasterrecoverytest', 'itms_app.view_disasterrecoverytest',
                
                # View Assets (for backup planning)
                'itms_app.view_asset', 'itms_app.view_location',
                
                # Custom Permissions
                'itms_app.can_export', 'itms_app.can_generate_reports'
            ]
        },
        
        'Reports_Viewers': {
            'description': 'ผู้ดูรายงาน - ดูรายงานและข้อมูลสถิติ',
            'color': '#64748b',  # Gray
            'permissions': [
                # Reporting & Analytics
                'itms_app.add_report', 'itms_app.change_report', 'itms_app.view_report',
                'itms_app.view_reportgeneration',
                
                # View All (Read Only)
                'itms_app.view_asset', 'itms_app.view_category', 'itms_app.view_location', 'itms_app.view_vendor',
                'itms_app.view_maintenancerecord', 'itms_app.view_softwarelicense', 'itms_app.view_softwareinstallation',
                'itms_app.view_helpdeskticket', 'itms_app.view_reservation',
                'itms_app.view_systemmonitoring', 'itms_app.view_alert',
                
                # Custom Permissions
                'itms_app.can_generate_reports', 'itms_app.can_export'
            ]
        },
        
        'End_Users': {
            'description': 'ผู้ใช้งานทั่วไป - สร้าง tickets และ reservations',
            'color': '#6b7280',  # Light Gray
            'permissions': [
                # Basic Operations
                'itms_app.add_helpdeskticket', 'itms_app.view_helpdeskticket',  # Own tickets only
                'itms_app.add_reservation', 'itms_app.view_reservation',  # Own reservations only
                
                # View Knowledge Base
                'itms_app.view_knowledgebase',
                
                # View own profile
                'auth.view_user'  # Restricted to own profile
            ]
        }
    }
    
    @classmethod
    def create_groups_and_permissions(cls):
        """
        สร้าง Groups และกำหนด Permissions ตาม PERMISSION_GROUPS
        """
        created_groups = []
        
        for group_name, group_data in cls.PERMISSION_GROUPS.items():
            # สร้างหรืออัพเดต Group
            group, created = Group.objects.get_or_create(
                name=group_name,
                defaults={'name': group_name}
            )
            
            if created:
                created_groups.append(group_name)
                print(f"✓ Created group: {group_name}")
            else:
                print(f"✓ Updated group: {group_name}")
            
            # Clear existing permissions
            group.permissions.clear()
            
            # กำหนด Permissions
            permissions_added = 0
            for perm_code in group_data['permissions']:
                if '*' in perm_code:  # Handle wildcard permissions
                    # Extract app_label and model
                    app_label, model_perm = perm_code.split('.', 1)
                    action, model = model_perm.split('_', 1)
                    
                    # Find all matching permissions
                    matching_perms = Permission.objects.filter(
                        content_type__app_label=app_label,
                        codename__startswith=action
                    )
                    
                    for perm in matching_perms:
                        group.permissions.add(perm)
                        permissions_added += 1
                        
                else:  # Handle specific permissions
                    try:
                        if '.' in perm_code:
                            app_label, codename = perm_code.split('.', 1)
                            
                            # Handle specific models for auth app to avoid duplicates
                            if app_label == 'auth':
                                if codename.startswith('add_user') or codename.startswith('change_user') or codename.startswith('delete_user') or codename.startswith('view_user'):
                                    model_name = 'user'
                                elif codename.startswith('add_group') or codename.startswith('change_group') or codename.startswith('delete_group') or codename.startswith('view_group'):
                                    model_name = 'group'  
                                elif codename.startswith('add_permission') or codename.startswith('change_permission') or codename.startswith('delete_permission') or codename.startswith('view_permission'):
                                    model_name = 'permission'
                                else:
                                    model_name = codename.split('_', 1)[1] if '_' in codename else 'user'
                                
                                content_type = ContentType.objects.filter(
                                    app_label=app_label, 
                                    model=model_name
                                ).first()
                            else:
                                content_type = ContentType.objects.filter(app_label=app_label).first()
                            
                            if content_type:
                                permission = Permission.objects.get(
                                    content_type=content_type,
                                    codename=codename
                                )
                            else:
                                print(f"  ! Content type not found for: {perm_code}")
                                continue
                        else:
                            permission = Permission.objects.get(codename=perm_code)
                        
                        group.permissions.add(permission)
                        permissions_added += 1
                        
                    except Permission.DoesNotExist:
                        print(f"  ! Permission not found: {perm_code}")
                        continue
                    except ContentType.DoesNotExist:
                        print(f"  ! Content type not found for: {perm_code}")
                        continue
            
            print(f"  → Added {permissions_added} permissions to {group_name}")
        
        return created_groups
    
    @classmethod
    def get_user_group_info(cls, user):
        """
        ดึงข้อมูล Groups ของ User พร้อมสีและคำอธิบาย
        """
        user_groups = user.groups.all()
        group_info = []
        
        for group in user_groups:
            if group.name in cls.PERMISSION_GROUPS:
                group_data = cls.PERMISSION_GROUPS[group.name]
                group_info.append({
                    'name': group.name,
                    'description': group_data['description'],
                    'color': group_data['color'],
                    'permissions_count': group.permissions.count()
                })
        
        return group_info
    
    @classmethod
    def get_group_summary(cls):
        """
        ดึงสรุป Groups ทั้งหมดในระบบ
        """
        summary = []
        
        for group_name, group_data in cls.PERMISSION_GROUPS.items():
            try:
                group = Group.objects.get(name=group_name)
                user_count = group.user_set.count()
                perm_count = group.permissions.count()
            except Group.DoesNotExist:
                user_count = 0
                perm_count = 0
            
            summary.append({
                'name': group_name,
                'description': group_data['description'],
                'color': group_data['color'],
                'user_count': user_count,
                'permissions_count': perm_count,
                'exists': Group.objects.filter(name=group_name).exists()
            })
        
        return summary


# Custom Permission Classes สำหรับ Django Admin
class ITMSAdminPermissionMixin:
    """
    Mixin สำหรับ Django Admin เพื่อตรวจสอบ permissions ขั้นสูง
    """
    
    def has_view_permission(self, request, obj=None):
        """Override view permission"""
        if request.user.is_superuser:
            return True
        
        # Check if user has view_all permission
        if request.user.has_perm(f'{self.model._meta.app_label}.can_view_all'):
            return True
        
        return super().has_view_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        """Override change permission"""
        if request.user.is_superuser:
            return True
        
        # Object-level permission check
        if obj and hasattr(obj, 'created_by'):
            if obj.created_by == request.user:
                return True
        
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Override delete permission"""
        if request.user.is_superuser:
            return True
        
        # Only allow deletion by IT Administrators
        if request.user.groups.filter(name='IT_Administrators').exists():
            return True
        
        return False
    
    def get_queryset(self, request):
        """Filter queryset based on user permissions"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        # If user has view_all permission, return all objects
        if request.user.has_perm(f'{self.model._meta.app_label}.can_view_all'):
            return qs
        
        # Filter by user's created objects or assigned objects
        if hasattr(self.model, 'created_by'):
            return qs.filter(created_by=request.user)
        elif hasattr(self.model, 'assigned_to'):
            return qs.filter(assigned_to=request.user)
        elif hasattr(self.model, 'requester'):
            return qs.filter(requester=request.user)
        
        return qs