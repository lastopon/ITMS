from django.urls import path
from . import views, api_views

urlpatterns = [
    # Web Views
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    # Asset Management
    path('assets/', views.assets_view, name='assets'),
    path('assets/<int:asset_id>/', views.asset_detail_view, name='asset_detail'),
    
    # Help Desk Management
    path('helpdesk/', views.helpdesk_view, name='helpdesk'),
    path('helpdesk/create/', views.create_ticket_view, name='create_ticket'),
    path('helpdesk/<int:ticket_id>/', views.ticket_detail_view, name='ticket_detail'),
    
    # Reservation Management
    path('reservations/', views.reservations_view, name='reservations'),
    path('reservations/create/', views.create_reservation_view, name='create_reservation'),
    path('reservations/<int:reservation_id>/', views.reservation_detail_view, name='reservation_detail'),
    
    # Software License Management
    path('software-licenses/', views.software_licenses_view, name='software_licenses'),
    path('software-licenses/create/', views.create_software_license_view, name='create_software_license'),
    path('software-licenses/<int:license_id>/', views.software_license_detail_view, name='software_license_detail'),
    
    # Maintenance Management
    path('maintenance/', views.maintenance_view, name='maintenance'),
    path('maintenance/create/', views.create_maintenance_record_view, name='create_maintenance'),
    path('maintenance/<int:record_id>/', views.maintenance_detail_view, name='maintenance_detail'),
    path('maintenance/schedule/', views.maintenance_schedule_view, name='maintenance_schedule'),
    
    # Vendor Management
    path('vendors/', views.vendors_view, name='vendors'),
    path('vendors/create/', views.create_vendor_view, name='create_vendor'),
    path('vendors/<int:vendor_id>/', views.vendor_detail_view, name='vendor_detail'),
    
    # API Views
    path('api/token/login/', api_views.api_login, name='api_login'),
    path('api/token/logout/', api_views.api_logout, name='api_logout'),
    path('api/user/profile/', api_views.api_user_profile, name='api_user_profile'),
]