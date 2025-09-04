"""
Management command สำหรับสร้าง Superuser พร้อมข้อมูลเริ่มต้น
ใช้คำสั่ง: python manage.py create_superuser --username admin --email admin@itms.local
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.permissions import ITMSPermissionManager

User = get_user_model()


class Command(BaseCommand):
    help = 'Create ITMS superuser with default settings'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Superuser username (default: admin)',
        )
        
        parser.add_argument(
            '--email',
            type=str,
            default='admin@itms.local',
            help='Superuser email (default: admin@itms.local)',
        )
        
        parser.add_argument(
            '--password',
            type=str,
            help='Superuser password (will be prompted if not provided)',
        )
        
        parser.add_argument(
            '--first-name',
            type=str,
            default='ITMS',
            help='First name (default: ITMS)',
        )
        
        parser.add_argument(
            '--last-name',
            type=str,
            default='Administrator',
            help='Last name (default: Administrator)',
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Force create even if user exists (will update existing user)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('👤 ITMS Superuser Creation Tool')
        )
        self.stdout.write('=' * 50)
        
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        force = options['force']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            if not force:
                self.stdout.write(
                    self.style.ERROR(f'❌ User "{username}" already exists. Use --force to update.')
                )
                return
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Updating existing user "{username}"')
                )
        
        # Get password if not provided
        if not password:
            password = self.get_password()
        
        try:
            with transaction.atomic():
                # Create or update user
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True,
                    }
                )
                
                if not created and force:
                    user.email = email
                    user.first_name = first_name
                    user.last_name = last_name
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                
                user.set_password(password)
                user.save()
                
                # Add user to IT_Administrators group
                try:
                    from django.contrib.auth.models import Group
                    admin_group = Group.objects.get(name='IT_Administrators')
                    admin_group.user_set.add(user)
                    group_status = '✅ Added to IT_Administrators group'
                except Group.DoesNotExist:
                    group_status = '⚠️  IT_Administrators group not found (run setup_permissions first)'
                
                action = 'created' if created else 'updated'
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Superuser "{username}" {action} successfully!')
                )
                
                # Display user information
                self.stdout.write('\n👤 User Information:')
                self.stdout.write(f'   Username: {user.username}')
                self.stdout.write(f'   Email: {user.email}')
                self.stdout.write(f'   Full Name: {user.get_full_name()}')
                self.stdout.write(f'   Staff Status: {"Yes" if user.is_staff else "No"}')
                self.stdout.write(f'   Superuser: {"Yes" if user.is_superuser else "No"}')
                self.stdout.write(f'   Active: {"Yes" if user.is_active else "No"}')
                self.stdout.write(f'   Groups: {group_status}')
                
                # Show admin URL
                self.stdout.write('\n🌐 Access Information:')
                self.stdout.write('   Admin URL: http://localhost:8000/admin/')
                self.stdout.write(f'   Login: {username}')
                self.stdout.write('   Password: [HIDDEN for security]')
                
                # Show group permissions if available
                if hasattr(ITMSPermissionManager, 'get_user_group_info'):
                    user_groups = ITMSPermissionManager.get_user_group_info(user)
                    if user_groups:
                        self.stdout.write('\n🔑 Assigned Groups:')
                        for group_info in user_groups:
                            self.stdout.write(
                                f'   • {group_info["name"]} - {group_info["description"]}'
                            )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating superuser: {e}')
            )
            raise
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Superuser creation completed!')
        )
    
    def get_password(self):
        """รับ password จากผู้ใช้"""
        import getpass
        
        while True:
            password1 = getpass.getpass('🔐 Enter password: ')
            if not password1:
                self.stdout.write(
                    self.style.ERROR('❌ Password cannot be empty')
                )
                continue
            
            if len(password1) < 8:
                self.stdout.write(
                    self.style.ERROR('❌ Password must be at least 8 characters long')
                )
                continue
            
            password2 = getpass.getpass('🔐 Confirm password: ')
            if password1 != password2:
                self.stdout.write(
                    self.style.ERROR('❌ Passwords do not match')
                )
                continue
            
            return password1