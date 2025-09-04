from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form for admin"""
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')

class CustomUserChangeForm(UserChangeForm):
    """Custom user change form for admin"""
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Enhanced User admin configuration for ITMS"""
    
    # Forms
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    
    # List display
    list_display = [
        'email', 'username', 'first_name', 'last_name', 
        'phone', 'is_active', 'is_staff', 'is_superuser', 'date_joined'
    ]
    
    # List filters
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 
        'date_joined', 'last_login', 'groups'
    ]
    
    # Search fields
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone']
    
    # Ordering
    ordering = ['email']
    
    # Readonly fields
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
    
    # Filter horizontal
    filter_horizontal = ['groups', 'user_permissions']
    
    # Fieldsets for editing existing users
    fieldsets = (
        (_('Personal Information'), {
            'fields': (
                'email', 'username', 'first_name', 'last_name', 
                'phone', 'profile_image'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets for adding new users
    add_fieldsets = (
        (_('Essential Information'), {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'password1', 'password2'
            ),
        }),
        (_('Additional Information'), {
            'classes': ('wide', 'collapse'),
            'fields': ('phone', 'profile_image'),
        }),
        (_('Permissions'), {
            'classes': ('wide', 'collapse'),
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    # Actions
    actions = ['make_active', 'make_inactive', 'make_staff', 'remove_staff']
    
    def make_active(self, request, queryset):
        """Activate selected users"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} users have been activated.')
    make_active.short_description = "✅ Activate selected users"
    
    def make_inactive(self, request, queryset):
        """Deactivate selected users"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} users have been deactivated.')
    make_inactive.short_description = "❌ Deactivate selected users"
    
    def make_staff(self, request, queryset):
        """Grant staff status to selected users"""
        count = queryset.update(is_staff=True)
        self.message_user(request, f'{count} users have been granted staff status.')
    make_staff.short_description = "👤 Grant staff status"
    
    def remove_staff(self, request, queryset):
        """Remove staff status from selected users"""
        count = queryset.update(is_staff=False)
        self.message_user(request, f'{count} users have had staff status removed.')
    remove_staff.short_description = "👤 Remove staff status"
    
    # Custom methods for display
    def get_queryset(self, request):
        """Optimize queryset with related fields"""
        return super().get_queryset(request).select_related().prefetch_related('groups')
    
    def get_full_name(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}".strip()
    get_full_name.short_description = "Full Name"
    
    def user_groups(self, obj):
        """Display user groups"""
        return ", ".join([group.name for group in obj.groups.all()]) or "No groups"
    user_groups.short_description = "Groups"