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

def list_users():
    User = get_user_model()
    
    print("=== All Users ===")
    users = User.objects.all()
    
    for user in users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is superuser: {user.is_superuser}")
        print(f"Is staff: {user.is_staff}")
        print(f"Is active: {user.is_active}")
        print("-" * 30)

if __name__ == '__main__':
    list_users()