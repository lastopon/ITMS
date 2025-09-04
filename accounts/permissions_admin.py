"""
Custom Permission Admin Classes for ITMS
"""
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.db.models import Q


@admin.register(Permission)
class ITMSPermissionAdmin(admin.ModelAdmin):
    """
    Enhanced Permission Admin with PostgreSQL-inspired interface
    """
    list_display = ['display_name', 'display_codename', 'display_content_type', 'display_app_label', 'usage_count']
    list_filter = [
        ('content_type__app_label', admin.SimpleListFilter),
        ('content_type__model', admin.SimpleListFilter),
        'content_type'
    ]
    search_fields = ['name', 'codename', 'content_type__app_label', 'content_type__model']
    list_per_page = 50
    
    # Custom filtering
    class AppLabelFilter(admin.SimpleListFilter):
        title = 'Application'
        parameter_name = 'app_label'
        
        def lookups(self, request, model_admin):
            apps = ContentType.objects.values_list('app_label', flat=True).distinct()
            return [(app, app.title()) for app in apps if app]
        
        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(content_type__app_label=self.value())
    
    class PermissionTypeFilter(admin.SimpleListFilter):
        title = 'Permission Type'
        parameter_name = 'perm_type'
        
        def lookups(self, request, model_admin):
            return [
                ('add', 'Add Permissions'),
                ('change', 'Change Permissions'),
                ('delete', 'Delete Permissions'),
                ('view', 'View Permissions'),
                ('custom', 'Custom Permissions'),
            ]
        
        def queryset(self, request, queryset):
            if self.value() == 'custom':
                return queryset.exclude(
                    Q(codename__startswith='add_') |
                    Q(codename__startswith='change_') |
                    Q(codename__startswith='delete_') |
                    Q(codename__startswith='view_')
                )
            elif self.value():
                return queryset.filter(codename__startswith=f'{self.value()}_')
    
    # Override list_filter with our custom filters
    list_filter = [AppLabelFilter, PermissionTypeFilter, 'content_type']
    
    def display_name(self, obj):
        """Display permission name with color coding"""
        color = self.get_permission_color(obj.codename)
        return format_html(
            '<span style="color: {}; font-weight: 500;">{}</span>',
            color,
            obj.name
        )
    display_name.short_description = 'Permission Name'
    display_name.admin_order_field = 'name'
    
    def display_codename(self, obj):
        """Display codename with badge styling"""
        badge_class = self.get_badge_class(obj.codename)
        return format_html(
            '<code class="{}"><strong>{}</strong></code>',
            badge_class,
            obj.codename
        )
    display_codename.short_description = 'Code Name'
    display_codename.admin_order_field = 'codename'
    
    def display_content_type(self, obj):
        """Display content type with app label"""
        return format_html(
            '<span style="color: #336791; font-weight: 500;">{}</span><br>'
            '<small style="color: #666;">{}</small>',
            obj.content_type.model.title(),
            obj.content_type.app_label
        )
    display_content_type.short_description = 'Content Type'
    display_content_type.admin_order_field = 'content_type'
    
    def display_app_label(self, obj):
        """Display app label with icon"""
        app_icons = {
            'itms_app': '🏢',
            'accounts': '👥', 
            'auth': '🔐',
            'admin': '⚙️',
            'contenttypes': '📋',
            'sessions': '🔑'
        }
        icon = app_icons.get(obj.content_type.app_label, '📦')
        
        return format_html(
            '{} <strong>{}</strong>',
            icon,
            obj.content_type.app_label.title()
        )
    display_app_label.short_description = 'Application'
    display_app_label.admin_order_field = 'content_type__app_label'
    
    def usage_count(self, obj):
        """Display how many groups use this permission"""
        count = obj.group_set.count()
        user_count = obj.user_set.count()
        
        if count > 0 or user_count > 0:
            return format_html(
                '<span style="background: #e8f5e8; padding: 2px 8px; border-radius: 12px; font-size: 11px;">'
                '👥 {} groups | 👤 {} users</span>',
                count, user_count
            )
        return format_html(
            '<span style="background: #fff3cd; padding: 2px 8px; border-radius: 12px; font-size: 11px; color: #856404;">'
            '⚠️ Unused</span>'
        )
    usage_count.short_description = 'Usage'
    
    def get_permission_color(self, codename):
        """Get color based on permission type"""
        if codename.startswith('add_'):
            return '#22c55e'  # Green for add
        elif codename.startswith('change_'):
            return '#3b82f6'  # Blue for change  
        elif codename.startswith('delete_'):
            return '#ef4444'  # Red for delete
        elif codename.startswith('view_'):
            return '#8b5cf6'  # Purple for view
        else:
            return '#f59e0b'  # Orange for custom
    
    def get_badge_class(self, codename):
        """Get CSS class for permission badge"""
        if codename.startswith('add_'):
            return 'pg-badge pg-badge-success'
        elif codename.startswith('change_'):
            return 'pg-badge pg-badge-primary'
        elif codename.startswith('delete_'):
            return 'pg-badge pg-badge-danger'
        elif codename.startswith('view_'):
            return 'pg-badge pg-badge-info'
        else:
            return 'pg-badge pg-badge-warning'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('content_type')
    
    def has_add_permission(self, request):
        """Prevent adding permissions directly"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting core permissions"""
        if obj and obj.content_type.app_label in ['auth', 'admin', 'contenttypes']:
            return False
        return super().has_delete_permission(request, obj)
    
    # Add custom CSS for permission badges
    class Media:
        css = {
            'all': ('admin/css/postgresql-theme.css',)
        }
        js = ('admin/js/permission-manager.js',)