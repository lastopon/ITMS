#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the project directory to the sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itms.settings')

# Configure Django
django.setup()

from django.contrib.auth import get_user_model

def create_user():
    User = get_user_model()
    
    # Create anurak user
    email = 'anurak@ghp.co.th'
    username = 'anurak'
    password = 'admin123'  # Same password as admin for simplicity
    
    try:
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            print(f'User with email {email} already exists')
            user = User.objects.get(email=email)
        elif User.objects.filter(username=username).exists():
            print(f'User with username {username} already exists')
            user = User.objects.get(username=username)
        else:
            # Create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f'Superuser created successfully!')
            print(f'Username: {username}')
            print(f'Email: {email}')
            print(f'Password: {password}')
        
        # Ensure user is superuser and staff
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print(f'User {username} is now a superuser with admin privileges')
        
    except Exception as e:
        print(f'Error creating user: {e}')

if __name__ == '__main__':
    create_user()