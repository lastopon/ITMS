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

from itms_app.models import Category, Location, Vendor

def setup_demo_data():
    print("Setting up demo data...")
    
    # Create Categories
    categories_data = [
        {'name': 'Computer Hardware', 'description': 'Desktops, laptops, servers'},
        {'name': 'Network Equipment', 'description': 'Routers, switches, access points'},
        {'name': 'Software Licenses', 'description': 'Operating systems and applications'},
        {'name': 'Mobile Devices', 'description': 'Smartphones, tablets'},
        {'name': 'Peripherals', 'description': 'Monitors, keyboards, printers'},
        {'name': 'Security Equipment', 'description': 'Cameras, access control systems'},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"✅ Created category: {category.name}")
        else:
            print(f"ℹ️  Category already exists: {category.name}")
    
    # Create Locations
    locations_data = [
        {'name': 'Head Office - Bangkok', 'address': '123 Sukhumvit Road, Bangkok 10110'},
        {'name': 'Branch Office - Chiang Mai', 'address': '456 Nimmanhemin Road, Chiang Mai 50200'},
        {'name': 'Data Center - Bangkok', 'address': '789 Ratchadaphisek Road, Bangkok 10400'},
        {'name': 'Warehouse - Samut Prakan', 'address': '321 Thepparat Road, Samut Prakan 10540'},
        {'name': 'Remote Office', 'address': 'Various remote locations'},
    ]
    
    for loc_data in locations_data:
        location, created = Location.objects.get_or_create(
            name=loc_data['name'],
            defaults={'address': loc_data['address']}
        )
        if created:
            print(f"✅ Created location: {location.name}")
        else:
            print(f"ℹ️  Location already exists: {location.name}")
    
    # Create Vendors
    vendors_data = [
        {
            'name': 'Dell Technologies',
            'contact_person': 'John Smith',
            'email': 'sales@dell.com',
            'phone': '02-123-4567'
        },
        {
            'name': 'HP Inc.',
            'contact_person': 'Jane Wilson',
            'email': 'business@hp.com',
            'phone': '02-234-5678'
        },
        {
            'name': 'Cisco Systems',
            'contact_person': 'Mike Johnson',
            'email': 'sales@cisco.com',
            'phone': '02-345-6789'
        },
        {
            'name': 'Microsoft Corporation',
            'contact_person': 'Sarah Brown',
            'email': 'licensing@microsoft.com',
            'phone': '02-456-7890'
        },
    ]
    
    for vendor_data in vendors_data:
        vendor, created = Vendor.objects.get_or_create(
            name=vendor_data['name'],
            defaults={
                'contact_person': vendor_data['contact_person'],
                'email': vendor_data['email'],
                'phone': vendor_data['phone']
            }
        )
        if created:
            print(f"✅ Created vendor: {vendor.name}")
        else:
            print(f"ℹ️  Vendor already exists: {vendor.name}")
    
    print("\n🎉 Demo data setup completed!")
    print("\nAvailable Categories:")
    for cat in Category.objects.all():
        print(f"  - {cat.name}")
    
    print("\nAvailable Locations:")
    for loc in Location.objects.all():
        print(f"  - {loc.name}")
    
    print("\nNow you can create Assets in Django Admin!")

if __name__ == '__main__':
    setup_demo_data()