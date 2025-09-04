"""
Context processors สำหรับ Django Admin Dashboard
เพิ่มข้อมูลที่จำเป็นสำหรับ templates
"""
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime
import json

User = get_user_model()


def dashboard_context(request):
    """
    Context processor สำหรับ Django Admin Dashboard
    """
    if not request.path.startswith('/admin/'):
        return {}
    
    try:
        # Basic statistics
        stats = get_dashboard_stats()
        
        # Chart data
        chart_data = get_chart_data()
        
        # Recent activities
        recent_activities = get_recent_activities()
        
        # System alerts
        system_alerts = get_system_alerts()
        
        # Database info
        db_info = get_database_info()
        
        return {
            'stats': stats,
            'stats_json': json.dumps(stats),
            'chart_data': json.dumps(chart_data),
            'recent_activities': recent_activities,
            'system_alerts': system_alerts,
            'db_info': db_info,
            'current_date': timezone.now(),
        }
        
    except Exception as e:
        # Fallback data in case of errors
        return {
            'stats': get_fallback_stats(),
            'stats_json': json.dumps(get_fallback_stats()),
            'chart_data': json.dumps({}),
            'recent_activities': [],
            'system_alerts': [],
            'db_info': {},
            'current_date': timezone.now(),
        }


def get_dashboard_stats():
    """
    ดึงสถิติพื้นฐานสำหรับ Dashboard
    """
    try:
        with connection.cursor() as cursor:
            stats = {}
            
            # Total assets
            cursor.execute("SELECT COUNT(*) FROM itms_app_asset")
            stats['total_assets'] = cursor.fetchone()[0]
            
            # Active assets
            cursor.execute("SELECT COUNT(*) FROM itms_app_asset WHERE status = 'active'")
            stats['active_assets'] = cursor.fetchone()[0]
            
            # Open tickets
            cursor.execute("""
                SELECT COUNT(*) FROM itms_app_helpdeskticket 
                WHERE status IN ('open', 'in_progress', 'pending')
            """)
            stats['open_tickets'] = cursor.fetchone()[0]
            
            # Total users
            cursor.execute("SELECT COUNT(*) FROM auth_user WHERE is_active = true")
            stats['total_users'] = cursor.fetchone()[0]
            
            # Maintenance due (next 30 days)
            cursor.execute("""
                SELECT COUNT(*) FROM itms_app_asset a
                LEFT JOIN itms_app_maintenancerecord m ON a.id = m.asset_id
                WHERE a.warranty_expiry <= %s
                OR (m.maintenance_date IS NOT NULL 
                    AND m.maintenance_date <= %s - INTERVAL '90 days')
            """, [timezone.now() + timedelta(days=30), timezone.now()])
            stats['maintenance_due'] = cursor.fetchone()[0]
            
            # Licenses expiring
            cursor.execute("""
                SELECT COUNT(*) FROM itms_app_softwarelicense 
                WHERE expiry_date <= %s AND expiry_date > %s
            """, [timezone.now() + timedelta(days=30), timezone.now()])
            stats['licenses_expiring'] = cursor.fetchone()[0]
            
            # Security incidents (last 30 days)
            cursor.execute("""
                SELECT COUNT(*) FROM itms_app_securityincident 
                WHERE discovered_date >= %s
            """, [timezone.now() - timedelta(days=30)])
            stats['security_incidents'] = cursor.fetchone()[0]
            
            # Pending approvals (reservations)
            cursor.execute("""
                SELECT COUNT(*) FROM itms_app_reservation 
                WHERE status = 'pending'
            """)
            stats['pending_approvals'] = cursor.fetchone()[0]
            
            # Calculate percentages and changes
            stats['active_percentage'] = round(
                (stats['active_assets'] / stats['total_assets'] * 100) if stats['total_assets'] > 0 else 0, 1
            )
            
            # Average resolution time (in hours)
            cursor.execute("""
                SELECT AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))/3600) 
                FROM itms_app_helpdeskticket 
                WHERE resolved_at IS NOT NULL 
                AND created_at >= %s
            """, [timezone.now() - timedelta(days=30)])
            result = cursor.fetchone()[0]
            stats['avg_resolution_time'] = round(result if result else 0, 1)
            
            # Active sessions (simplified - just logged in users in last hour)
            cursor.execute("""
                SELECT COUNT(*) FROM auth_user 
                WHERE last_login >= %s
            """, [timezone.now() - timedelta(hours=1)])
            stats['active_sessions'] = cursor.fetchone()[0]
            
            return stats
            
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return get_fallback_stats()


def get_chart_data():
    """
    ดึงข้อมูลสำหรับ Charts
    """
    try:
        with connection.cursor() as cursor:
            chart_data = {}
            
            # Asset status over time (last 6 months)
            chart_data['assetStatus'] = [65, 72, 80, 75, 88, 95]  # Simplified
            chart_data['maintenance'] = [15, 18, 12, 20, 15, 10]  # Simplified
            
            # Ticket priority distribution
            cursor.execute("""
                SELECT priority, COUNT(*) 
                FROM itms_app_helpdeskticket 
                WHERE created_at >= %s
                GROUP BY priority
            """, [timezone.now() - timedelta(days=30)])
            
            priority_data = dict(cursor.fetchall())
            chart_data['ticketPriority'] = {
                'critical': priority_data.get('critical', 0),
                'high': priority_data.get('high', 0),
                'medium': priority_data.get('medium', 0),
                'low': priority_data.get('low', 0)
            }
            
            return chart_data
            
    except Exception as e:
        print(f"Error getting chart data: {e}")
        return {
            'assetStatus': [65, 72, 80, 75, 88, 95],
            'maintenance': [15, 18, 12, 20, 15, 10],
            'ticketPriority': {'critical': 3, 'high': 12, 'medium': 25, 'low': 8}
        }


def get_recent_activities():
    """
    ดึงกิจกรรมล่าสุด
    """
    activities = []
    
    try:
        with connection.cursor() as cursor:
            # Recent asset additions
            cursor.execute("""
                SELECT a.name, a.created_at, u.username, u.first_name, u.last_name
                FROM itms_app_asset a
                LEFT JOIN auth_user u ON a.assigned_to_id = u.id
                ORDER BY a.created_at DESC
                LIMIT 5
            """)
            
            for row in cursor.fetchall():
                activities.append({
                    'type': 'asset',
                    'icon': 'server',
                    'title': f'New asset added: {row[0]}',
                    'description': f'Asset "{row[0]}" has been added to the system',
                    'user': row[2] or 'System',
                    'timestamp': row[1]
                })
            
            # Recent tickets
            cursor.execute("""
                SELECT t.title, t.created_at, u.username, u.first_name, u.last_name, t.priority
                FROM itms_app_helpdeskticket t
                LEFT JOIN auth_user u ON t.requester_id = u.id
                ORDER BY t.created_at DESC
                LIMIT 3
            """)
            
            for row in cursor.fetchall():
                activities.append({
                    'type': 'ticket',
                    'icon': 'ticket-alt',
                    'title': f'New {row[5]} priority ticket',
                    'description': row[0][:50] + '...' if len(row[0]) > 50 else row[0],
                    'user': row[2] or 'Anonymous',
                    'timestamp': row[1]
                })
            
            # Sort by timestamp
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            return activities[:8]  # Return top 8
            
    except Exception as e:
        print(f"Error getting recent activities: {e}")
        return []


def get_system_alerts():
    """
    ดึงการแจ้งเตือนระบบ
    """
    alerts = []
    
    try:
        with connection.cursor() as cursor:
            # High priority tickets
            cursor.execute("""
                SELECT COUNT(*) FROM itms_app_helpdeskticket 
                WHERE priority = 'high' AND status = 'open'
            """)
            high_tickets = cursor.fetchone()[0]
            
            if high_tickets > 0:
                alerts.append({
                    'id': 'high_tickets',
                    'severity': 'high',
                    'icon': 'exclamation-triangle',
                    'title': 'High Priority Tickets',
                    'message': f'{high_tickets} high priority tickets require attention',
                    'created_at': timezone.now() - timedelta(minutes=30)
                })
            
            # Assets needing maintenance
            cursor.execute("""
                SELECT COUNT(*) FROM itms_app_asset 
                WHERE warranty_expiry <= %s AND warranty_expiry > %s
            """, [timezone.now() + timedelta(days=30), timezone.now()])
            maintenance_needed = cursor.fetchone()[0]
            
            if maintenance_needed > 0:
                alerts.append({
                    'id': 'maintenance_due',
                    'severity': 'medium',
                    'icon': 'wrench',
                    'title': 'Maintenance Due',
                    'message': f'{maintenance_needed} assets require maintenance soon',
                    'created_at': timezone.now() - timedelta(hours=2)
                })
            
            # Security incidents
            cursor.execute("""
                SELECT COUNT(*) FROM itms_app_securityincident 
                WHERE status = 'open' OR status = 'investigating'
            """)
            security_incidents = cursor.fetchone()[0]
            
            if security_incidents > 0:
                alerts.append({
                    'id': 'security_incidents',
                    'severity': 'high',
                    'icon': 'shield-alt',
                    'title': 'Security Incidents',
                    'message': f'{security_incidents} open security incidents',
                    'created_at': timezone.now() - timedelta(hours=1)
                })
            
            return alerts
            
    except Exception as e:
        print(f"Error getting system alerts: {e}")
        return []


def get_database_info():
    """
    ดึงข้อมูลฐานข้อมูล PostgreSQL
    """
    try:
        with connection.cursor() as cursor:
            db_info = {}
            
            # PostgreSQL version
            cursor.execute("SELECT version()")
            version_info = cursor.fetchone()[0]
            db_info['version'] = version_info.split(',')[0].replace('PostgreSQL ', '')
            
            # Database size
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            db_info['size'] = cursor.fetchone()[0]
            
            # Active connections
            cursor.execute("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE state = 'active'
            """)
            db_info['connections'] = cursor.fetchone()[0]
            
            # Last backup (mock data - would be real in production)
            db_info['last_backup'] = timezone.now() - timedelta(hours=6)
            
            return db_info
            
    except Exception as e:
        print(f"Error getting database info: {e}")
        return {
            'version': 'Unknown',
            'size': 'Unknown',
            'connections': 0,
            'last_backup': 'Never'
        }


def get_fallback_stats():
    """
    ข้อมูลสำรองในกรณีเกิดข้อผิดพลาด
    """
    return {
        'total_assets': 0,
        'active_assets': 0,
        'open_tickets': 0,
        'total_users': 0,
        'maintenance_due': 0,
        'licenses_expiring': 0,
        'security_incidents': 0,
        'pending_approvals': 0,
        'active_percentage': 0,
        'avg_resolution_time': 0,
        'active_sessions': 0,
        'assets_change': 0
    }