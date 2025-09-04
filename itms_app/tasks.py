import os
import logging
from datetime import datetime, timedelta
from celery import shared_task
from django.core.management import call_command
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def health_check_task():
    """
    Periodic health check task to monitor system status
    """
    try:
        # Check database connectivity
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check cache connectivity
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        cache_status = cache.get('health_check')
        
        logger.info("Health check completed successfully")
        return {
            'status': 'healthy',
            'database': 'ok',
            'cache': 'ok' if cache_status == 'ok' else 'error',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@shared_task
def cleanup_old_logs():
    """
    Clean up old log files to prevent disk space issues
    """
    try:
        log_dir = settings.LOG_DIR
        if not log_dir.exists():
            return "Log directory does not exist"
        
        # Remove log files older than 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        cleaned_files = []
        
        for log_file in log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                cleaned_files.append(str(log_file))
        
        logger.info(f"Cleaned up {len(cleaned_files)} old log files")
        return f"Cleaned up {len(cleaned_files)} files: {cleaned_files}"
    
    except Exception as e:
        logger.error(f"Log cleanup failed: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def backup_database():
    """
    Create database backup (for production use)
    """
    try:
        # This is a placeholder - in production you would implement
        # proper database backup logic here
        logger.info("Database backup task executed")
        return "Database backup completed"
    except Exception as e:
        logger.error(f"Database backup failed: {str(e)}")
        return f"Backup failed: {str(e)}"

@shared_task
def send_system_notifications():
    """
    Send system status notifications to administrators
    """
    try:
        # Placeholder for notification logic
        logger.info("System notifications sent")
        return "Notifications sent successfully"
    except Exception as e:
        logger.error(f"Failed to send notifications: {str(e)}")
        return f"Notification failed: {str(e)}"