from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import validate_email
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db import models
from datetime import datetime, timedelta
import re


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        login_input = request.POST.get('email', '').strip()  # Can be email or username
        password = request.POST.get('password', '').strip()
        remember_me = request.POST.get('remember_me')
        
        if not login_input or not password:
            messages.error(request, 'Please provide both username/email and password.')
            return render(request, 'accounts/login.html')
        
        # Try to find user by email first, then by username
        user = None
        try:
            if '@' in login_input:
                # If input contains @, treat as email
                user = User.objects.get(email=login_input)
            else:
                # Otherwise, treat as username
                user = User.objects.get(username=login_input)
        except User.DoesNotExist:
            # If first attempt failed, try the other method
            try:
                if '@' in login_input:
                    user = User.objects.get(username=login_input)
                else:
                    user = User.objects.get(email=login_input)
            except User.DoesNotExist:
                pass
        
        if user:
            # Authenticate using email (since USERNAME_FIELD = 'email')
            authenticated_user = authenticate(request, username=user.email, password=password)
            
            if authenticated_user is not None:
                if authenticated_user.is_active:
                    login(request, authenticated_user)
                    
                    # Handle "Remember Me" functionality
                    if remember_me:
                        request.session.set_expiry(1209600)  # 2 weeks
                    else:
                        request.session.set_expiry(0)  # Browser close
                    
                    # Update last login
                    authenticated_user.last_login = timezone.now()
                    authenticated_user.save(update_fields=['last_login'])
                    
                    messages.success(request, f'Welcome back, {authenticated_user.first_name or authenticated_user.username}!')
                    
                    # Redirect to next page if available
                    next_page = request.GET.get('next', 'dashboard')
                    return redirect(next_page)
                else:
                    messages.error(request, 'Your account has been deactivated. Please contact administrator.')
            else:
                messages.error(request, 'Invalid username/email or password.')
        else:
            messages.error(request, 'Invalid username/email or password.')
    
    return render(request, 'accounts/login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Validation
        errors = []
        
        # Check required fields
        if not all([email, username, password, confirm_password, first_name, last_name]):
            errors.append('All required fields must be filled.')
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            errors.append('Please enter a valid email address.')
        
        # Check username format
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')
        
        if len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        
        # Password validation
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if not re.search(r'[A-Za-z]', password):
            errors.append('Password must contain at least one letter.')
        
        if not re.search(r'[0-9]', password):
            errors.append('Password must contain at least one number.')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            errors.append('An account with this email already exists.')
        
        if User.objects.filter(username=username).exists():
            errors.append('This username is already taken.')
        
        # Phone validation (if provided)
        if phone and not re.match(r'^\+?[1-9]\d{1,14}$', phone):
            errors.append('Please enter a valid phone number.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/login.html')
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone if phone else None
                )
                
                messages.success(request, f'Welcome {first_name}! Your account has been created successfully. Please login.')
                return redirect('login')
                
        except Exception as e:
            messages.error(request, 'An error occurred while creating your account. Please try again.')
    
    return render(request, 'accounts/login.html')


@login_required
def dashboard(request):
    from itms_app.models import Asset, HelpDeskTicket, SoftwareLicense, MaintenanceRecord, Category, Location, Vendor
    from django.db.models import Count, Q, Sum
    from datetime import datetime, timedelta
    
    # Get current date for time-based calculations
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Asset statistics
    total_assets = Asset.objects.count()
    active_assets = Asset.objects.filter(status='active').count()
    maintenance_assets = Asset.objects.filter(status='maintenance').count()
    retired_assets = Asset.objects.filter(status='retired').count()
    disposed_assets = Asset.objects.filter(status='disposed').count()
    inactive_assets = Asset.objects.filter(status='inactive').count()
    
    # Ticket statistics
    total_tickets = HelpDeskTicket.objects.count()
    open_tickets = HelpDeskTicket.objects.filter(status='open').count()
    in_progress_tickets = HelpDeskTicket.objects.filter(status='in_progress').count()
    resolved_tickets = HelpDeskTicket.objects.filter(status='resolved').count()
    closed_tickets = HelpDeskTicket.objects.filter(status='closed').count()
    pending_tickets = HelpDeskTicket.objects.filter(status='pending').count()
    
    # Critical and high priority tickets
    critical_tickets = HelpDeskTicket.objects.filter(priority='critical', status__in=['open', 'in_progress']).count()
    high_priority_tickets = HelpDeskTicket.objects.filter(priority='high', status__in=['open', 'in_progress']).count()
    
    # Software license statistics  
    total_licenses = SoftwareLicense.objects.count()
    expiring_licenses = SoftwareLicense.objects.filter(
        expiry_date__lte=now + timedelta(days=30),
        expiry_date__gte=now
    ).count()
    
    # License utilization
    license_utilization = SoftwareLicense.objects.aggregate(
        total_installations=Sum('max_installations'),
        current_installations=Sum('current_installations')
    )
    
    # Maintenance statistics
    total_maintenance = MaintenanceRecord.objects.count()
    recent_maintenance_count = MaintenanceRecord.objects.filter(
        maintenance_date__gte=thirty_days_ago
    ).count()
    
    # Recent maintenance records
    recent_maintenance = MaintenanceRecord.objects.select_related(
        'asset', 'performed_by'
    ).order_by('-maintenance_date')[:5]
    
    # Recent tickets (all tickets, not just assigned to user)
    recent_tickets = HelpDeskTicket.objects.select_related(
        'requester', 'assigned_to', 'category', 'asset'
    ).order_by('-created_at')[:5]
    
    # User's assigned tickets
    my_tickets = HelpDeskTicket.objects.filter(
        assigned_to=request.user
    ).select_related('requester', 'category', 'asset').order_by('-created_at')[:5]
    
    # Asset category breakdown
    asset_categories = Asset.objects.values(
        'category__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Asset status breakdown  
    asset_status_data = Asset.objects.values('status').annotate(count=Count('status'))
    
    # Recent asset additions
    new_assets_count = Asset.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # System overview stats
    total_categories = Category.objects.count()
    total_locations = Location.objects.count() 
    total_vendors = Vendor.objects.count()
    
    # Build context
    context = {
        'user': request.user,
        
        # Asset statistics
        'total_assets': total_assets,
        'active_assets': active_assets,
        'maintenance_assets': maintenance_assets,
        'retired_assets': retired_assets,
        'disposed_assets': disposed_assets,
        'inactive_assets': inactive_assets,
        'new_assets_count': new_assets_count,
        
        # Ticket statistics
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'pending_tickets': pending_tickets,
        'critical_tickets': critical_tickets,
        'high_priority_tickets': high_priority_tickets,
        
        # Software licenses
        'total_licenses': total_licenses,
        'expiring_licenses': expiring_licenses,
        'license_utilization': license_utilization,
        
        # Maintenance
        'total_maintenance': total_maintenance,
        'recent_maintenance_count': recent_maintenance_count,
        'recent_maintenance': recent_maintenance,
        
        # Activity data
        'recent_tickets': recent_tickets,
        'my_tickets': my_tickets,
        
        # Breakdown data
        'asset_categories': asset_categories,
        'asset_status_data': asset_status_data,
        
        # System stats
        'total_categories': total_categories,
        'total_locations': total_locations,
        'total_vendors': total_vendors,
        
        # Time-based data
        'current_time': now,
        'thirty_days_ago': thirty_days_ago,
    }
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def assets_view(request):
    from itms_app.models import Asset, Category, Location, Vendor
    from django.db.models import Q
    from django.core.paginator import Paginator
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    location_filter = request.GET.get('location', '')
    
    # Base queryset
    assets = Asset.objects.select_related('category', 'location', 'vendor', 'assigned_to').all()
    
    # Apply filters
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(asset_tag__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(model__icontains=search_query)
        )
    
    if category_filter:
        assets = assets.filter(category_id=category_filter)
    
    if status_filter:
        assets = assets.filter(status=status_filter)
        
    if location_filter:
        assets = assets.filter(location_id=location_filter)
    
    # Pagination
    paginator = Paginator(assets, 12)  # 12 assets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    categories = Category.objects.all()
    locations = Location.objects.all()
    status_choices = Asset.ASSET_STATUS_CHOICES
    
    context = {
        'user': request.user,
        'page_obj': page_obj,
        'assets': page_obj,
        'categories': categories,
        'locations': locations,
        'status_choices': status_choices,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'location_filter': location_filter,
        'total_assets': assets.count(),
    }
    
    return render(request, 'accounts/assets.html', context)


@login_required
def asset_detail_view(request, asset_id):
    from itms_app.models import Asset, MaintenanceRecord
    from django.shortcuts import get_object_or_404
    
    asset = get_object_or_404(Asset, id=asset_id)
    maintenance_records = MaintenanceRecord.objects.filter(asset=asset).select_related('performed_by').order_by('-maintenance_date')[:5]
    
    context = {
        'user': request.user,
        'asset': asset,
        'maintenance_records': maintenance_records,
    }
    
    return render(request, 'accounts/asset_detail.html', context)


@login_required
def helpdesk_view(request):
    from itms_app.models import HelpDeskTicket, Category, Asset
    from django.db.models import Q
    from django.core.paginator import Paginator
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    assigned_filter = request.GET.get('assigned', '')
    
    # Base queryset
    tickets = HelpDeskTicket.objects.select_related(
        'requester', 'assigned_to', 'category', 'asset'
    ).all()
    
    # Apply filters
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) |
            Q(ticket_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requester__first_name__icontains=search_query) |
            Q(requester__last_name__icontains=search_query)
        )
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
        
    if category_filter:
        tickets = tickets.filter(category_id=category_filter)
        
    if assigned_filter == 'me':
        tickets = tickets.filter(assigned_to=request.user)
    elif assigned_filter == 'unassigned':
        tickets = tickets.filter(assigned_to__isnull=True)
    
    # Pagination
    paginator = Paginator(tickets, 10)  # 10 tickets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    categories = Category.objects.all()
    status_choices = HelpDeskTicket.STATUS_CHOICES
    priority_choices = HelpDeskTicket.PRIORITY_CHOICES
    
    context = {
        'user': request.user,
        'page_obj': page_obj,
        'tickets': page_obj,
        'categories': categories,
        'status_choices': status_choices,
        'priority_choices': priority_choices,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'assigned_filter': assigned_filter,
        'total_tickets': tickets.count(),
    }
    
    return render(request, 'accounts/helpdesk.html', context)


@login_required
def ticket_detail_view(request, ticket_id):
    from itms_app.models import HelpDeskTicket
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    
    ticket = get_object_or_404(HelpDeskTicket, id=ticket_id)
    
    # Handle status updates
    if request.method == 'POST':
        new_status = request.POST.get('status')
        resolution = request.POST.get('resolution', '')
        
        if new_status and new_status in [choice[0] for choice in HelpDeskTicket.STATUS_CHOICES]:
            old_status = ticket.status
            ticket.status = new_status
            
            if new_status == 'resolved' and resolution:
                ticket.resolution = resolution
            
            # Assign to current user if taking ownership
            if new_status == 'in_progress' and not ticket.assigned_to:
                ticket.assigned_to = request.user
            
            ticket.save()
            messages.success(request, f'Ticket status updated from {old_status} to {new_status}')
            return redirect('ticket_detail', ticket_id=ticket.id)
    
    context = {
        'user': request.user,
        'ticket': ticket,
        'status_choices': HelpDeskTicket.STATUS_CHOICES,
    }
    
    return render(request, 'accounts/ticket_detail.html', context)


@login_required
def create_ticket_view(request):
    from itms_app.models import HelpDeskTicket, Category, Asset
    from django.contrib import messages
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'medium')
        category_id = request.POST.get('category')
        asset_id = request.POST.get('asset') or None
        
        # Validation
        errors = []
        
        if not title:
            errors.append('Title is required.')
        if not description:
            errors.append('Description is required.')
        if not category_id:
            errors.append('Category is required.')
            
        if len(title) < 5:
            errors.append('Title must be at least 5 characters long.')
            
        if len(description) < 10:
            errors.append('Description must be at least 10 characters long.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                category = Category.objects.get(id=category_id)
                asset = None
                if asset_id:
                    asset = Asset.objects.get(id=asset_id)
                
                ticket = HelpDeskTicket.objects.create(
                    title=title,
                    description=description,
                    priority=priority,
                    category=category,
                    asset=asset,
                    requester=request.user,
                    status='open'
                )
                
                messages.success(request, f'Ticket {ticket.ticket_number} created successfully!')
                return redirect('ticket_detail', ticket_id=ticket.id)
                
            except Exception as e:
                messages.error(request, f'Error creating ticket: {str(e)}')
    
    # Get form options
    categories = Category.objects.all()
    assets = Asset.objects.filter(status='active').select_related('category')
    priority_choices = HelpDeskTicket.PRIORITY_CHOICES
    
    context = {
        'user': request.user,
        'categories': categories,
        'assets': assets,
        'priority_choices': priority_choices,
    }
    
    return render(request, 'accounts/create_ticket.html', context)


@login_required
def reservations_view(request):
    from itms_app.models import Reservation, Asset, Category
    
    # Get filter parameters
    search = request.GET.get('search', '').strip()
    asset_filter = request.GET.get('asset', '').strip()
    type_filter = request.GET.get('type', '').strip()
    status_filter = request.GET.get('status', '').strip()
    date_filter = request.GET.get('date', '').strip()
    
    # Base queryset
    reservations = Reservation.objects.select_related('asset', 'reserved_by', 'approved_by').all()
    
    # Apply filters
    if search:
        reservations = reservations.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(reservation_number__icontains=search) |
            Q(asset__name__icontains=search) |
            Q(reserved_by__email__icontains=search)
        )
    
    if asset_filter:
        reservations = reservations.filter(asset_id=asset_filter)
    
    if type_filter:
        reservations = reservations.filter(reservation_type=type_filter)
    
    if status_filter:
        reservations = reservations.filter(status=status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            reservations = reservations.filter(start_datetime__date=filter_date)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(reservations, 10)
    page_number = request.GET.get('page', 1)
    reservations_page = paginator.get_page(page_number)
    
    # Get filter options
    reservable_assets = Asset.objects.filter(
        status='active',
        category__name__in=['Meeting Room', 'Vehicle', 'Equipment']
    ).select_related('category')
    
    reservation_types = Reservation.RESERVATION_TYPE_CHOICES
    status_choices = Reservation.RESERVATION_STATUS_CHOICES
    
    # Get counts for dashboard
    total_reservations = Reservation.objects.count()
    pending_reservations = Reservation.objects.filter(status='pending').count()
    approved_reservations = Reservation.objects.filter(status='approved').count()
    active_reservations = Reservation.objects.filter(
        status='approved',
        start_datetime__lte=timezone.now(),
        end_datetime__gte=timezone.now()
    ).count()
    
    context = {
        'user': request.user,
        'reservations': reservations_page,
        'search': search,
        'asset_filter': asset_filter,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'reservable_assets': reservable_assets,
        'reservation_types': reservation_types,
        'status_choices': status_choices,
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'approved_reservations': approved_reservations,
        'active_reservations': active_reservations,
    }
    
    return render(request, 'accounts/reservations.html', context)


@login_required
def create_reservation_view(request):
    from itms_app.models import Reservation, Asset, Category
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        asset_id = request.POST.get('asset', '').strip()
        reservation_type = request.POST.get('reservation_type', '').strip()
        start_datetime = request.POST.get('start_datetime', '').strip()
        end_datetime = request.POST.get('end_datetime', '').strip()
        number_of_people = request.POST.get('number_of_people', '').strip()
        purpose = request.POST.get('purpose', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        special_requirements = request.POST.get('special_requirements', '').strip()
        
        # Validation
        errors = []
        
        if not title:
            errors.append('Title is required.')
        elif len(title) < 5:
            errors.append('Title must be at least 5 characters long.')
        
        if not asset_id:
            errors.append('Please select an asset to reserve.')
        
        if not reservation_type:
            errors.append('Please select a reservation type.')
        
        if not start_datetime:
            errors.append('Start date and time is required.')
        
        if not end_datetime:
            errors.append('End date and time is required.')
        
        # Validate datetime formats and logic
        start_dt = None
        end_dt = None
        if start_datetime:
            try:
                start_dt = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
                start_dt = timezone.make_aware(start_dt)
            except ValueError:
                errors.append('Invalid start date/time format.')
        
        if end_datetime:
            try:
                end_dt = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M')
                end_dt = timezone.make_aware(end_dt)
            except ValueError:
                errors.append('Invalid end date/time format.')
        
        if start_dt and end_dt:
            if end_dt <= start_dt:
                errors.append('End time must be after start time.')
            
            if start_dt < timezone.now():
                errors.append('Start time cannot be in the past.')
            
            # Check for conflicts
            try:
                asset = Asset.objects.get(id=asset_id)
                conflicts = Reservation.objects.filter(
                    asset=asset,
                    status__in=['pending', 'approved'],
                    start_datetime__lt=end_dt,
                    end_datetime__gt=start_dt
                )
                
                if conflicts.exists():
                    errors.append(f'Asset "{asset.name}" is already reserved during this time period.')
            except Asset.DoesNotExist:
                errors.append('Selected asset does not exist.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                asset = Asset.objects.get(id=asset_id)
                
                reservation = Reservation.objects.create(
                    title=title,
                    description=description,
                    asset=asset,
                    reserved_by=request.user,
                    reservation_type=reservation_type,
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    number_of_people=int(number_of_people) if number_of_people else None,
                    purpose=purpose,
                    contact_phone=contact_phone,
                    special_requirements=special_requirements,
                    status='pending'
                )
                
                messages.success(request, f'Reservation {reservation.reservation_number} created successfully!')
                return redirect('reservation_detail', reservation_id=reservation.id)
                
            except Exception as e:
                messages.error(request, f'Error creating reservation: {str(e)}')
    
    # Get form options
    reservable_assets = Asset.objects.filter(
        status='active',
        category__name__in=['Meeting Room', 'Vehicle', 'Equipment']
    ).select_related('category')
    
    reservation_types = Reservation.RESERVATION_TYPE_CHOICES
    
    context = {
        'user': request.user,
        'reservable_assets': reservable_assets,
        'reservation_types': reservation_types,
    }
    
    return render(request, 'accounts/create_reservation.html', context)


@login_required
def reservation_detail_view(request, reservation_id):
    from itms_app.models import Reservation
    
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Handle status updates (for staff only or reservation owner for cancellation)
    if request.method == 'POST':
        new_status = request.POST.get('status', '').strip()
        approval_notes = request.POST.get('approval_notes', '').strip()
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        
        can_update = False
        
        if request.user.is_staff:
            can_update = True
        elif request.user == reservation.reserved_by and new_status == 'cancelled':
            can_update = reservation.can_be_cancelled()
        
        if can_update and new_status in [choice[0] for choice in Reservation.RESERVATION_STATUS_CHOICES]:
            old_status = reservation.status
            reservation.status = new_status
            
            if new_status == 'approved' and request.user.is_staff:
                reservation.approved_by = request.user
                reservation.approval_notes = approval_notes
            elif new_status == 'rejected' and request.user.is_staff:
                reservation.rejection_reason = rejection_reason
            
            reservation.save()
            
            if new_status != old_status:
                messages.success(request, f'Reservation status updated to {reservation.get_status_display()}.')
            
            return redirect('reservation_detail', reservation_id=reservation.id)
        else:
            messages.error(request, 'You do not have permission to update this reservation.')
    
    # Check for conflicts if approved
    conflicts = []
    if reservation.status == 'approved':
        conflicts = Reservation.objects.filter(
            asset=reservation.asset,
            status='approved',
            start_datetime__lt=reservation.end_datetime,
            end_datetime__gt=reservation.start_datetime
        ).exclude(id=reservation.id)
    
    context = {
        'user': request.user,
        'reservation': reservation,
        'conflicts': conflicts,
        'status_choices': Reservation.RESERVATION_STATUS_CHOICES,
        'can_cancel': reservation.can_be_cancelled() and request.user == reservation.reserved_by,
        'can_approve': request.user.is_staff and reservation.status == 'pending',
    }
    
    return render(request, 'accounts/reservation_detail.html', context)


@login_required
def software_licenses_view(request):
    from itms_app.models import SoftwareLicense, SoftwareInstallation, Vendor
    
    # Get filter parameters
    search = request.GET.get('search', '').strip()
    vendor_filter = request.GET.get('vendor', '').strip()
    status_filter = request.GET.get('status', '').strip()  # active, expired, expiring
    license_type_filter = request.GET.get('license_type', '').strip()
    
    # Base queryset
    licenses = SoftwareLicense.objects.select_related('vendor').all()
    
    # Apply filters
    if search:
        licenses = licenses.filter(
            Q(name__icontains=search) |
            Q(version__icontains=search) |
            Q(license_key__icontains=search) |
            Q(vendor__name__icontains=search)
        )
    
    if vendor_filter:
        licenses = licenses.filter(vendor_id=vendor_filter)
    
    if license_type_filter:
        licenses = licenses.filter(license_type__icontains=license_type_filter)
    
    # Status filtering
    today = timezone.now().date()
    if status_filter == 'active':
        licenses = licenses.filter(
            Q(expiry_date__isnull=True) | Q(expiry_date__gt=today)
        )
    elif status_filter == 'expired':
        licenses = licenses.filter(expiry_date__lt=today)
    elif status_filter == 'expiring':
        # Expiring within 30 days
        from datetime import timedelta
        expiring_date = today + timedelta(days=30)
        licenses = licenses.filter(expiry_date__lte=expiring_date, expiry_date__gt=today)
    
    # Pagination
    paginator = Paginator(licenses, 12)
    page_number = request.GET.get('page', 1)
    licenses_page = paginator.get_page(page_number)
    
    # Get filter options
    vendors = Vendor.objects.all().order_by('name')
    license_types = SoftwareLicense.objects.values_list('license_type', flat=True).distinct()
    
    # Get statistics
    total_licenses = SoftwareLicense.objects.count()
    active_licenses = SoftwareLicense.objects.filter(
        Q(expiry_date__isnull=True) | Q(expiry_date__gt=today)
    ).count()
    expired_licenses = SoftwareLicense.objects.filter(expiry_date__lt=today).count()
    from datetime import timedelta
    expiring_soon = SoftwareLicense.objects.filter(
        expiry_date__lte=today + timedelta(days=30),
        expiry_date__gt=today
    ).count()
    
    # Calculate total installations
    total_installations = SoftwareInstallation.objects.count()
    total_cost = SoftwareLicense.objects.aggregate(
        total=models.Sum('cost')
    )['total'] or 0
    
    context = {
        'user': request.user,
        'licenses': licenses_page,
        'search': search,
        'vendor_filter': vendor_filter,
        'status_filter': status_filter,
        'license_type_filter': license_type_filter,
        'vendors': vendors,
        'license_types': license_types,
        'total_licenses': total_licenses,
        'active_licenses': active_licenses,
        'expired_licenses': expired_licenses,
        'expiring_soon': expiring_soon,
        'total_installations': total_installations,
        'total_cost': total_cost,
    }
    
    return render(request, 'accounts/software_licenses.html', context)


@login_required
def software_license_detail_view(request, license_id):
    from itms_app.models import SoftwareLicense, SoftwareInstallation, Asset
    
    license = get_object_or_404(SoftwareLicense, id=license_id)
    
    # Get installations for this license
    installations = SoftwareInstallation.objects.filter(
        software_license=license
    ).select_related('asset', 'installed_by').order_by('-installation_date')
    
    # Handle new installation
    if request.method == 'POST' and 'install' in request.POST:
        asset_id = request.POST.get('asset_id')
        notes = request.POST.get('installation_notes', '').strip()
        
        if asset_id:
            try:
                asset = Asset.objects.get(id=asset_id)
                
                # Check if already installed on this asset
                if not SoftwareInstallation.objects.filter(
                    software_license=license, asset=asset
                ).exists():
                    
                    # Check available installations
                    if license.available_installations > 0:
                        installation = SoftwareInstallation.objects.create(
                            software_license=license,
                            asset=asset,
                            installed_by=request.user,
                            installation_date=timezone.now(),
                            notes=notes
                        )
                        
                        # Update current installations count
                        license.current_installations += 1
                        license.save()
                        
                        messages.success(request, f'Software successfully installed on {asset.name}')
                    else:
                        messages.error(request, 'No available installations remaining for this license')
                else:
                    messages.error(request, f'Software is already installed on {asset.name}')
                    
            except Asset.DoesNotExist:
                messages.error(request, 'Selected asset does not exist')
        
        return redirect('software_license_detail', license_id=license.id)
    
    # Handle uninstall
    if request.method == 'POST' and 'uninstall' in request.POST:
        installation_id = request.POST.get('installation_id')
        
        if installation_id:
            try:
                installation = SoftwareInstallation.objects.get(
                    id=installation_id,
                    software_license=license
                )
                asset_name = installation.asset.name
                installation.delete()
                
                # Update current installations count
                license.current_installations = max(0, license.current_installations - 1)
                license.save()
                
                messages.success(request, f'Software uninstalled from {asset_name}')
                
            except SoftwareInstallation.DoesNotExist:
                messages.error(request, 'Installation not found')
        
        return redirect('software_license_detail', license_id=license.id)
    
    # Get available assets for installation
    installed_asset_ids = installations.values_list('asset_id', flat=True)
    available_assets = Asset.objects.filter(
        status='active'
    ).exclude(id__in=installed_asset_ids).order_by('name')
    
    # Check license status
    today = timezone.now().date()
    is_expired = license.expiry_date and license.expiry_date < today
    days_to_expire = None
    if license.expiry_date and not is_expired:
        days_to_expire = (license.expiry_date - today).days
    
    context = {
        'user': request.user,
        'license': license,
        'installations': installations,
        'available_assets': available_assets,
        'is_expired': is_expired,
        'days_to_expire': days_to_expire,
    }
    
    return render(request, 'accounts/software_license_detail.html', context)


@login_required
def create_software_license_view(request):
    from itms_app.models import SoftwareLicense, Vendor
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        version = request.POST.get('version', '').strip()
        vendor_id = request.POST.get('vendor', '').strip()
        license_key = request.POST.get('license_key', '').strip()
        license_type = request.POST.get('license_type', '').strip()
        purchase_date = request.POST.get('purchase_date', '').strip()
        expiry_date = request.POST.get('expiry_date', '').strip()
        cost = request.POST.get('cost', '').strip()
        max_installations = request.POST.get('max_installations', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Software name is required.')
        elif len(name) < 2:
            errors.append('Software name must be at least 2 characters long.')
        
        if not vendor_id:
            errors.append('Please select a vendor.')
        
        if not license_type:
            errors.append('License type is required.')
        
        if not purchase_date:
            errors.append('Purchase date is required.')
        
        if not cost:
            errors.append('Cost is required.')
        elif not cost.replace('.', '').isdigit():
            errors.append('Cost must be a valid number.')
        
        if not max_installations:
            errors.append('Maximum installations is required.')
        elif not max_installations.isdigit():
            errors.append('Maximum installations must be a number.')
        elif int(max_installations) < 1:
            errors.append('Maximum installations must be at least 1.')
        
        # Validate dates
        purchase_dt = None
        expiry_dt = None
        
        if purchase_date:
            try:
                purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid purchase date format.')
        
        if expiry_date:
            try:
                expiry_dt = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                if purchase_dt and expiry_dt <= purchase_dt:
                    errors.append('Expiry date must be after purchase date.')
            except ValueError:
                errors.append('Invalid expiry date format.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                vendor = Vendor.objects.get(id=vendor_id)
                
                license = SoftwareLicense.objects.create(
                    name=name,
                    version=version,
                    vendor=vendor,
                    license_key=license_key,
                    license_type=license_type,
                    purchase_date=purchase_dt,
                    expiry_date=expiry_dt,
                    cost=float(cost),
                    max_installations=int(max_installations),
                    notes=notes
                )
                
                messages.success(request, f'Software license "{license.name}" created successfully!')
                return redirect('software_license_detail', license_id=license.id)
                
            except Exception as e:
                messages.error(request, f'Error creating license: {str(e)}')
    
    # Get form options
    vendors = Vendor.objects.all().order_by('name')
    common_license_types = [
        'Per User',
        'Per Device',
        'Site License',
        'Enterprise License',
        'Academic License',
        'Concurrent License',
        'Subscription',
        'Perpetual License'
    ]
    
    context = {
        'user': request.user,
        'vendors': vendors,
        'common_license_types': common_license_types,
    }
    
    return render(request, 'accounts/create_software_license.html', context)


@login_required
def maintenance_view(request):
    from itms_app.models import MaintenanceRecord, Asset, Vendor
    
    # Get filter parameters
    search = request.GET.get('search', '').strip()
    asset_filter = request.GET.get('asset', '').strip()
    type_filter = request.GET.get('type', '').strip()
    vendor_filter = request.GET.get('vendor', '').strip()
    date_filter = request.GET.get('date', '').strip()
    performed_by_filter = request.GET.get('performed_by', '').strip()
    
    # Base queryset
    records = MaintenanceRecord.objects.select_related(
        'asset', 'performed_by', 'vendor'
    ).all()
    
    # Apply filters
    if search:
        records = records.filter(
            Q(description__icontains=search) |
            Q(notes__icontains=search) |
            Q(asset__name__icontains=search) |
            Q(asset__asset_tag__icontains=search) |
            Q(performed_by__email__icontains=search)
        )
    
    if asset_filter:
        records = records.filter(asset_id=asset_filter)
    
    if type_filter:
        records = records.filter(maintenance_type=type_filter)
    
    if vendor_filter:
        records = records.filter(vendor_id=vendor_filter)
    
    if performed_by_filter:
        records = records.filter(performed_by_id=performed_by_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            records = records.filter(maintenance_date__date=filter_date)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page', 1)
    records_page = paginator.get_page(page_number)
    
    # Get filter options
    assets = Asset.objects.filter(status='active').order_by('name')
    vendors = Vendor.objects.all().order_by('name')
    performed_by_users = User.objects.filter(
        maintenancerecord__isnull=False
    ).distinct().order_by('email')
    
    # Get statistics
    total_records = MaintenanceRecord.objects.count()
    this_month_records = MaintenanceRecord.objects.filter(
        maintenance_date__year=timezone.now().year,
        maintenance_date__month=timezone.now().month
    ).count()
    
    # Maintenance type counts
    preventive_count = MaintenanceRecord.objects.filter(maintenance_type='preventive').count()
    corrective_count = MaintenanceRecord.objects.filter(maintenance_type='corrective').count()
    emergency_count = MaintenanceRecord.objects.filter(maintenance_type='emergency').count()
    
    # Cost statistics
    total_cost = MaintenanceRecord.objects.filter(
        cost__isnull=False
    ).aggregate(total=models.Sum('cost'))['total'] or 0
    
    avg_cost = MaintenanceRecord.objects.filter(
        cost__isnull=False
    ).aggregate(avg=models.Avg('cost'))['avg'] or 0
    
    # Recent maintenance (assets that need attention)
    from datetime import timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_assets = Asset.objects.filter(
        maintenance_records__maintenance_date__gte=thirty_days_ago
    ).distinct().count()
    
    overdue_assets = Asset.objects.exclude(
        maintenance_records__maintenance_date__gte=thirty_days_ago
    ).filter(status='active').count()
    
    context = {
        'user': request.user,
        'records': records_page,
        'search': search,
        'asset_filter': asset_filter,
        'type_filter': type_filter,
        'vendor_filter': vendor_filter,
        'date_filter': date_filter,
        'performed_by_filter': performed_by_filter,
        'assets': assets,
        'vendors': vendors,
        'performed_by_users': performed_by_users,
        'total_records': total_records,
        'this_month_records': this_month_records,
        'preventive_count': preventive_count,
        'corrective_count': corrective_count,
        'emergency_count': emergency_count,
        'total_cost': total_cost,
        'avg_cost': avg_cost,
        'recent_assets': recent_assets,
        'overdue_assets': overdue_assets,
    }
    
    return render(request, 'accounts/maintenance.html', context)


@login_required
def create_maintenance_record_view(request):
    from itms_app.models import MaintenanceRecord, Asset, Vendor
    
    if request.method == 'POST':
        asset_id = request.POST.get('asset', '').strip()
        maintenance_type = request.POST.get('maintenance_type', '').strip()
        description = request.POST.get('description', '').strip()
        maintenance_date = request.POST.get('maintenance_date', '').strip()
        cost = request.POST.get('cost', '').strip()
        vendor_id = request.POST.get('vendor', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        # Validation
        errors = []
        
        if not asset_id:
            errors.append('Please select an asset.')
        
        if not maintenance_type:
            errors.append('Please select maintenance type.')
        
        if not description:
            errors.append('Description is required.')
        elif len(description) < 10:
            errors.append('Description must be at least 10 characters long.')
        
        if not maintenance_date:
            errors.append('Maintenance date is required.')
        
        # Validate date
        maintenance_dt = None
        if maintenance_date:
            try:
                maintenance_dt = datetime.strptime(maintenance_date, '%Y-%m-%dT%H:%M')
                maintenance_dt = timezone.make_aware(maintenance_dt)
            except ValueError:
                errors.append('Invalid maintenance date format.')
        
        # Validate cost
        cost_value = None
        if cost:
            try:
                cost_value = float(cost)
                if cost_value < 0:
                    errors.append('Cost cannot be negative.')
            except ValueError:
                errors.append('Invalid cost format.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                asset = Asset.objects.get(id=asset_id)
                vendor = None
                if vendor_id:
                    vendor = Vendor.objects.get(id=vendor_id)
                
                record = MaintenanceRecord.objects.create(
                    asset=asset,
                    maintenance_type=maintenance_type,
                    description=description,
                    performed_by=request.user,
                    maintenance_date=maintenance_dt,
                    cost=cost_value,
                    vendor=vendor,
                    notes=notes
                )
                
                messages.success(request, f'Maintenance record created successfully for {asset.name}!')
                return redirect('maintenance_detail', record_id=record.id)
                
            except Exception as e:
                messages.error(request, f'Error creating maintenance record: {str(e)}')
    
    # Get form options
    assets = Asset.objects.filter(status='active').order_by('name')
    vendors = Vendor.objects.all().order_by('name')
    maintenance_types = MaintenanceRecord.MAINTENANCE_TYPE_CHOICES
    
    context = {
        'user': request.user,
        'assets': assets,
        'vendors': vendors,
        'maintenance_types': maintenance_types,
    }
    
    return render(request, 'accounts/create_maintenance.html', context)


@login_required
def maintenance_detail_view(request, record_id):
    from itms_app.models import MaintenanceRecord
    
    record = get_object_or_404(MaintenanceRecord, id=record_id)
    
    # Handle record updates (for staff or record creator)
    if request.method == 'POST':
        if request.user.is_staff or request.user == record.performed_by:
            description = request.POST.get('description', '').strip()
            cost = request.POST.get('cost', '').strip()
            notes = request.POST.get('notes', '').strip()
            
            if description and len(description) >= 10:
                record.description = description
                
                # Update cost if provided
                if cost:
                    try:
                        cost_value = float(cost)
                        if cost_value >= 0:
                            record.cost = cost_value
                    except ValueError:
                        messages.error(request, 'Invalid cost format.')
                        return redirect('maintenance_detail', record_id=record.id)
                
                record.notes = notes
                record.save()
                
                messages.success(request, 'Maintenance record updated successfully!')
            else:
                messages.error(request, 'Description must be at least 10 characters long.')
        else:
            messages.error(request, 'You do not have permission to update this record.')
        
        return redirect('maintenance_detail', record_id=record.id)
    
    # Get related maintenance records for the same asset
    related_records = MaintenanceRecord.objects.filter(
        asset=record.asset
    ).exclude(id=record.id).order_by('-maintenance_date')[:5]
    
    # Calculate days since maintenance
    days_since = (timezone.now().date() - record.maintenance_date.date()).days
    
    context = {
        'user': request.user,
        'record': record,
        'related_records': related_records,
        'days_since': days_since,
        'can_edit': request.user.is_staff or request.user == record.performed_by,
    }
    
    return render(request, 'accounts/maintenance_detail.html', context)


@login_required
def maintenance_schedule_view(request):
    from itms_app.models import MaintenanceRecord, Asset
    from datetime import timedelta
    
    # Get upcoming and overdue maintenance
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    ninety_days_ago = today - timedelta(days=90)
    
    # Assets that haven't had maintenance in 30 days (overdue)
    overdue_assets = Asset.objects.filter(
        status='active'
    ).exclude(
        maintenance_records__maintenance_date__gte=thirty_days_ago
    ).annotate(
        last_maintenance=models.Max('maintenance_records__maintenance_date')
    ).order_by('last_maintenance')
    
    # Assets that haven't had maintenance in 90 days (critical)
    critical_assets = Asset.objects.filter(
        status='active'
    ).exclude(
        maintenance_records__maintenance_date__gte=ninety_days_ago
    ).annotate(
        last_maintenance=models.Max('maintenance_records__maintenance_date')
    ).order_by('last_maintenance')
    
    # Recent maintenance records
    recent_records = MaintenanceRecord.objects.select_related(
        'asset', 'performed_by'
    ).order_by('-maintenance_date')[:10]
    
    # Maintenance statistics by type for the last 30 days
    last_30_days = today - timedelta(days=30)
    recent_preventive = MaintenanceRecord.objects.filter(
        maintenance_type='preventive',
        maintenance_date__gte=last_30_days
    ).count()
    
    recent_corrective = MaintenanceRecord.objects.filter(
        maintenance_type='corrective',
        maintenance_date__gte=last_30_days
    ).count()
    
    recent_emergency = MaintenanceRecord.objects.filter(
        maintenance_type='emergency',
        maintenance_date__gte=last_30_days
    ).count()
    
    # Calculate maintenance statistics with percentages
    maintenance_total = recent_preventive + recent_corrective + recent_emergency
    preventive_percent = int((recent_preventive * 100 / maintenance_total)) if maintenance_total > 0 else 0
    corrective_percent = int((recent_corrective * 100 / maintenance_total)) if maintenance_total > 0 else 0
    emergency_percent = int((recent_emergency * 100 / maintenance_total)) if maintenance_total > 0 else 0
    
    # Calculate monthly statistics
    this_month_maintenance = MaintenanceRecord.objects.filter(
        maintenance_date__year=timezone.now().year,
        maintenance_date__month=timezone.now().month
    ).count()
    
    # Calculate recent maintenance cost
    recent_maintenance_cost = MaintenanceRecord.objects.filter(
        maintenance_date__gte=last_30_days
    ).aggregate(total_cost=models.Sum('cost'))['total_cost'] or 0
    
    context = {
        'user': request.user,
        'overdue_assets': overdue_assets[:20],  # Limit to 20
        'critical_assets': critical_assets[:10],  # Limit to 10
        'recent_maintenance': recent_records,
        'this_month_maintenance': this_month_maintenance,
        'recent_maintenance_cost': recent_maintenance_cost,
        'maintenance_stats': {
            'preventive': recent_preventive,
            'corrective': recent_corrective,
            'emergency': recent_emergency,
            'total': maintenance_total,
            'preventive_percent': preventive_percent,
            'corrective_percent': corrective_percent,
            'emergency_percent': emergency_percent,
        }
    }
    
    return render(request, 'accounts/maintenance_schedule.html', context)


@login_required
def vendors_view(request):
    from itms_app.models import Vendor, Asset, SoftwareLicense, MaintenanceRecord
    from django.db.models import Count, Sum, Q
    from django.core.paginator import Paginator
    
    # Get filter parameters
    search = request.GET.get('search', '').strip()
    has_assets = request.GET.get('has_assets', '').strip()
    has_licenses = request.GET.get('has_licenses', '').strip()
    has_maintenance = request.GET.get('has_maintenance', '').strip()
    sort_by = request.GET.get('sort', 'name')
    
    # Base queryset with annotations
    vendors = Vendor.objects.annotate(
        assets_count=Count('asset', distinct=True),
        licenses_count=Count('softwarelicense', distinct=True),
        maintenance_count=Count('maintenancerecord', distinct=True),
        total_license_cost=Sum('softwarelicense__cost'),
        total_maintenance_cost=Sum('maintenancerecord__cost')
    )
    
    # Apply search filter
    if search:
        vendors = vendors.filter(
            Q(name__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Apply filters
    if has_assets == 'yes':
        vendors = vendors.filter(assets_count__gt=0)
    elif has_assets == 'no':
        vendors = vendors.filter(assets_count=0)
        
    if has_licenses == 'yes':
        vendors = vendors.filter(licenses_count__gt=0)
    elif has_licenses == 'no':
        vendors = vendors.filter(licenses_count=0)
        
    if has_maintenance == 'yes':
        vendors = vendors.filter(maintenance_count__gt=0)
    elif has_maintenance == 'no':
        vendors = vendors.filter(maintenance_count=0)
    
    # Apply sorting
    sort_options = {
        'name': 'name',
        'assets': '-assets_count',
        'licenses': '-licenses_count',
        'maintenance': '-maintenance_count',
        'cost': '-total_license_cost'
    }
    if sort_by in sort_options:
        vendors = vendors.order_by(sort_options[sort_by])
    else:
        vendors = vendors.order_by('name')
    
    # Pagination
    paginator = Paginator(vendors, 12)
    page_number = request.GET.get('page', 1)
    vendors_page = paginator.get_page(page_number)
    
    # Calculate statistics
    total_vendors = Vendor.objects.count()
    vendors_with_assets = Vendor.objects.annotate(
        assets_count=Count('asset')
    ).filter(assets_count__gt=0).count()
    
    vendors_with_licenses = Vendor.objects.annotate(
        licenses_count=Count('softwarelicense')
    ).filter(licenses_count__gt=0).count()
    
    vendors_with_maintenance = Vendor.objects.annotate(
        maintenance_count=Count('maintenancerecord')
    ).filter(maintenance_count__gt=0).count()
    
    total_license_spending = SoftwareLicense.objects.aggregate(
        total=Sum('cost')
    )['total'] or 0
    
    total_maintenance_spending = MaintenanceRecord.objects.aggregate(
        total=Sum('cost')
    )['total'] or 0
    
    context = {
        'vendors': vendors_page,
        'total_vendors': total_vendors,
        'vendors_with_assets': vendors_with_assets,
        'vendors_with_licenses': vendors_with_licenses,
        'vendors_with_maintenance': vendors_with_maintenance,
        'total_license_spending': total_license_spending,
        'total_maintenance_spending': total_maintenance_spending,
        'total_spending': total_license_spending + total_maintenance_spending,
        'search': search,
        'has_assets': has_assets,
        'has_licenses': has_licenses,
        'has_maintenance': has_maintenance,
        'sort_by': sort_by,
    }
    
    return render(request, 'accounts/vendors.html', context)


@login_required
def vendor_detail_view(request, vendor_id):
    from itms_app.models import Vendor, Asset, SoftwareLicense, MaintenanceRecord
    from django.db.models import Sum, Q
    from django.shortcuts import get_object_or_404
    from datetime import datetime, timedelta
    
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    # Check if user can edit (staff users only)
    can_edit = request.user.is_staff
    
    # Handle form submission for editing
    if request.method == 'POST' and can_edit:
        vendor.name = request.POST.get('name', vendor.name)
        vendor.contact_person = request.POST.get('contact_person', vendor.contact_person)
        vendor.email = request.POST.get('email', vendor.email)
        vendor.phone = request.POST.get('phone', vendor.phone)
        vendor.address = request.POST.get('address', vendor.address)
        
        try:
            vendor.save()
            messages.success(request, 'Vendor information updated successfully!')
            return redirect('vendor_detail', vendor_id=vendor.id)
        except Exception as e:
            messages.error(request, f'Error updating vendor: {str(e)}')
    
    # Get related assets
    assets = Asset.objects.filter(vendor=vendor).order_by('-created_at')
    
    # Get software licenses
    licenses = SoftwareLicense.objects.filter(vendor=vendor).order_by('-created_at')
    
    # Get maintenance records
    maintenance_records = MaintenanceRecord.objects.filter(
        vendor=vendor
    ).select_related('asset', 'performed_by').order_by('-maintenance_date')[:10]
    
    # Calculate financial statistics
    license_spending = licenses.aggregate(total=Sum('cost'))['total'] or 0
    maintenance_spending = maintenance_records.aggregate(total=Sum('cost'))['total'] or 0
    
    # Recent activity (last 30 days)
    last_30_days = timezone.now() - timedelta(days=30)
    recent_maintenance = MaintenanceRecord.objects.filter(
        vendor=vendor,
        maintenance_date__gte=last_30_days
    ).count()
    
    # License statistics
    total_license_value = license_spending
    active_licenses = licenses.filter(
        Q(expiry_date__isnull=True) | Q(expiry_date__gte=timezone.now().date())
    ).count()
    expired_licenses = licenses.filter(
        expiry_date__lt=timezone.now().date()
    ).count()
    
    context = {
        'vendor': vendor,
        'can_edit': can_edit,
        'assets': assets,
        'licenses': licenses,
        'maintenance_records': maintenance_records,
        'assets_count': assets.count(),
        'licenses_count': licenses.count(),
        'maintenance_count': maintenance_records.count(),
        'license_spending': license_spending,
        'maintenance_spending': maintenance_spending,
        'total_spending': license_spending + maintenance_spending,
        'recent_maintenance': recent_maintenance,
        'total_license_value': total_license_value,
        'active_licenses': active_licenses,
        'expired_licenses': expired_licenses,
    }
    
    return render(request, 'accounts/vendor_detail.html', context)


@login_required
def create_vendor_view(request):
    from itms_app.models import Vendor
    
    if request.method == 'POST':
        errors = []
        form_data = request.POST
        
        # Get form data
        name = form_data.get('name', '').strip()
        contact_person = form_data.get('contact_person', '').strip()
        email = form_data.get('email', '').strip()
        phone = form_data.get('phone', '').strip()
        address = form_data.get('address', '').strip()
        
        # Validation
        if not name:
            errors.append('Vendor name is required')
        
        if email and not '@' in email:
            errors.append('Please enter a valid email address')
        
        # Check for duplicate vendor name
        if Vendor.objects.filter(name__iexact=name).exists():
            errors.append('A vendor with this name already exists')
        
        if not errors:
            try:
                vendor = Vendor.objects.create(
                    name=name,
                    contact_person=contact_person,
                    email=email,
                    phone=phone,
                    address=address
                )
                messages.success(request, f'Vendor "{vendor.name}" created successfully!')
                return redirect('vendor_detail', vendor_id=vendor.id)
            except Exception as e:
                errors.append(f'Error creating vendor: {str(e)}')
        
        # If there are errors, return to form with data
        if errors:
            context = {
                'errors': errors,
                'form_data': form_data,
            }
            return render(request, 'accounts/create_vendor.html', context)
    
    return render(request, 'accounts/create_vendor.html')


def logout_view(request):
    logout(request)
    return redirect('login')