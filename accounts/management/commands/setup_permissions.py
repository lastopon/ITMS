"""
Management command สำหรับตั้งค่า Permissions และ Groups
ใช้คำสั่ง: python manage.py setup_permissions
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.conf import settings
from accounts.permissions import ITMSPermissionManager
import sys


class Command(BaseCommand):
    help = 'Setup ITMS permission groups and assign default permissions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            dest='reset',
            help='Reset all groups and permissions (WARNING: This will remove existing group assignments)',
        )
        
        parser.add_argument(
            '--create-demo-users',
            action='store_true',
            dest='create_demo_users',
            help='Create demo users for each group',
        )
        
        parser.add_argument(
            '--show-summary',
            action='store_true',
            dest='show_summary',
            help='Show summary of all groups and permissions',
        )
        
        parser.add_argument(
            '--assign-user',
            type=str,
            dest='assign_user',
            help='Username to assign to a group (use with --to-group)',
        )
        
        parser.add_argument(
            '--to-group',
            type=str,
            dest='to_group',
            help='Group name to assign user to (use with --assign-user)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 ITMS Permission Setup Tool')
        )
        self.stdout.write('=' * 50)
        
        if options['reset']:
            self.reset_permissions()
        
        if options['show_summary']:
            self.show_summary()
            return
        
        if options['assign_user'] and options['to_group']:
            self.assign_user_to_group(options['assign_user'], options['to_group'])
            return
        
        # Main setup process
        self.setup_permissions()
        
        if options['create_demo_users']:
            self.create_demo_users()
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Permission setup completed successfully!')
        )
    
    def reset_permissions(self):
        """ลบ Groups และ Permissions ทั้งหมด (ใช้อย่างระวัง!)"""
        if not self.confirm_action('This will DELETE ALL GROUPS and remove user assignments. Continue?'):
            return
        
        self.stdout.write(
            self.style.WARNING('🗑️  Resetting permissions...')
        )
        
        with transaction.atomic():
            # Remove all users from groups
            for group_name in ITMSPermissionManager.PERMISSION_GROUPS.keys():
                try:
                    group = Group.objects.get(name=group_name)
                    group.user_set.clear()
                    group.delete()
                    self.stdout.write(f'   ✓ Deleted group: {group_name}')
                except Group.DoesNotExist:
                    pass
        
        self.stdout.write(
            self.style.SUCCESS('✅ Reset completed')
        )
    
    @transaction.atomic
    def setup_permissions(self):
        """ตั้งค่า Permissions และ Groups"""
        self.stdout.write(
            self.style.HTTP_INFO('📋 Setting up permission groups...')
        )
        
        # Create groups and assign permissions
        created_groups = ITMSPermissionManager.create_groups_and_permissions()
        
        self.stdout.write('\n📊 Setup Summary:')
        for group_name, group_data in ITMSPermissionManager.PERMISSION_GROUPS.items():
            try:
                group = Group.objects.get(name=group_name)
                user_count = group.user_set.count()
                perm_count = group.permissions.count()
                
                status = '🆕 NEW' if group_name in created_groups else '✅ UPDATED'
                
                self.stdout.write(
                    f'   {status} {group_name:<20} | '
                    f'👥 {user_count:>2} users | '
                    f'🔑 {perm_count:>3} permissions | '
                    f'{group_data["description"]}'
                )
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Failed to create: {group_name}')
                )
    
    def create_demo_users(self):
        """สร้าง Demo Users สำหรับแต่ละ Group"""
        if not self.confirm_action('Create demo users for each group?'):
            return
        
        self.stdout.write(
            self.style.HTTP_INFO('\n👤 Creating demo users...')
        )
        
        demo_users = {
            'IT_Administrators': {
                'username': 'admin_demo',
                'email': 'admin@itms.local',
                'first_name': 'Admin',
                'last_name': 'Demo',
                'is_staff': True,
                'is_superuser': False
            },
            'Asset_Managers': {
                'username': 'asset_manager',
                'email': 'asset.manager@itms.local',
                'first_name': 'Asset',
                'last_name': 'Manager',
                'is_staff': True
            },
            'Security_Officers': {
                'username': 'security_officer',
                'email': 'security@itms.local',
                'first_name': 'Security',
                'last_name': 'Officer',
                'is_staff': True
            },
            'Network_Engineers': {
                'username': 'network_engineer',
                'email': 'network@itms.local',
                'first_name': 'Network',
                'last_name': 'Engineer',
                'is_staff': True
            },
            'Helpdesk_Staff': {
                'username': 'helpdesk_staff',
                'email': 'helpdesk@itms.local',
                'first_name': 'Helpdesk',
                'last_name': 'Staff',
                'is_staff': True
            },
            'End_Users': {
                'username': 'end_user',
                'email': 'user@itms.local',
                'first_name': 'End',
                'last_name': 'User',
                'is_staff': False
            }
        }
        
        default_password = 'demo123456'
        
        for group_name, user_data in demo_users.items():
            try:
                # Create user if doesn't exist
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data['email'],
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'is_staff': user_data.get('is_staff', False),
                        'is_superuser': user_data.get('is_superuser', False)
                    }
                )
                
                if created:
                    user.set_password(default_password)
                    user.save()
                    status = '🆕 CREATED'
                else:
                    status = '✅ EXISTS'
                
                # Add user to group
                try:
                    group = Group.objects.get(name=group_name)
                    group.user_set.add(user)
                    
                    self.stdout.write(
                        f'   {status} {user.username:<15} → {group_name} '
                        f'({user.email})'
                    )
                    
                except Group.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'   ❌ Group not found: {group_name}')
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Failed to create user {user_data["username"]}: {e}')
                )
        
        self.stdout.write(
            self.style.WARNING(f'\n🔐 Default password for demo users: {default_password}')
        )
        self.stdout.write(
            self.style.WARNING('⚠️  Please change passwords before production use!')
        )
    
    def show_summary(self):
        """แสดงสรุปข้อมูล Groups และ Permissions"""
        self.stdout.write(
            self.style.SUCCESS('📊 ITMS Permission Groups Summary')
        )
        self.stdout.write('=' * 80)
        
        summary = ITMSPermissionManager.get_group_summary()
        
        for group_info in summary:
            status_icon = '✅' if group_info['exists'] else '❌'
            color = group_info['color']
            
            self.stdout.write(
                f"\n{status_icon} {group_info['name']:<25} "
                f"({color})"
            )
            self.stdout.write(f"   📝 {group_info['description']}")
            self.stdout.write(
                f"   👥 Users: {group_info['user_count']:<3} | "
                f"🔑 Permissions: {group_info['permissions_count']:<3}"
            )
            
            if group_info['exists']:
                # Show users in this group
                try:
                    group = Group.objects.get(name=group_info['name'])
                    users = group.user_set.all()
                    if users:
                        user_list = ', '.join([f"{u.username} ({u.get_full_name()})" for u in users[:5]])
                        if len(users) > 5:
                            user_list += f" ... and {len(users) - 5} more"
                        self.stdout.write(f"   👤 Users: {user_list}")
                    else:
                        self.stdout.write("   👤 Users: None")
                except Group.DoesNotExist:
                    pass
        
        # PostgreSQL Connection Info
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(
            self.style.HTTP_INFO('🐘 PostgreSQL Database Information')
        )
        
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                db_version = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        tableowner 
                    FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename LIKE 'auth_%' OR tablename LIKE 'itms_%'
                    LIMIT 5
                """)
                tables = cursor.fetchall()
                
                self.stdout.write(f"   📊 Version: {db_version.split(',')[0]}")
                self.stdout.write(f"   📋 Tables: {len(tables)} permission-related tables")
                
                # Show current database stats
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                user_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM auth_group")
                group_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM auth_permission")
                permission_count = cursor.fetchone()[0]
                
                self.stdout.write(f"   👥 Total Users: {user_count}")
                self.stdout.write(f"   🏷️  Total Groups: {group_count}")
                self.stdout.write(f"   🔑 Total Permissions: {permission_count}")
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"   ⚠️  Could not fetch database info: {e}")
            )
    
    def assign_user_to_group(self, username, group_name):
        """กำหนด User เข้า Group"""
        try:
            user = User.objects.get(username=username)
            group = Group.objects.get(name=group_name)
            
            if group_name not in ITMSPermissionManager.PERMISSION_GROUPS:
                self.stdout.write(
                    self.style.ERROR(f'❌ Invalid group name: {group_name}')
                )
                self.stdout.write('Available groups:')
                for gname in ITMSPermissionManager.PERMISSION_GROUPS.keys():
                    self.stdout.write(f'   - {gname}')
                return
            
            if group.user_set.filter(id=user.id).exists():
                self.stdout.write(
                    self.style.WARNING(f'⚠️  User {username} is already in group {group_name}')
                )
                return
            
            group.user_set.add(user)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully added {username} to {group_name}'
                )
            )
            
            # Show user's new groups
            user_groups = ITMSPermissionManager.get_user_group_info(user)
            self.stdout.write(f"\n👤 {user.get_full_name()} ({user.username}) groups:")
            for group_info in user_groups:
                self.stdout.write(
                    f"   • {group_info['name']} - {group_info['description']}"
                )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ User not found: {username}')
            )
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Group not found: {group_name}')
            )
    
    def confirm_action(self, message):
        """ขอการยืนยันจากผู้ใช้"""
        response = input(f"\n❓ {message} [y/N]: ")
        return response.lower() in ['y', 'yes']