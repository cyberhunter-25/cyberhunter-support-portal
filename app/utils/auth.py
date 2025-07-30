"""
Authentication utilities
"""
from flask import request
from flask_login import current_user
from app.extensions import login_manager
from app.models import User, AdminUser


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    # Check if it's an admin user (prefixed with 'admin_')
    if user_id.startswith('admin_'):
        admin_id = user_id.replace('admin_', '')
        return AdminUser.query.get(int(admin_id))
    else:
        return User.query.get(int(user_id))


def get_client_ip():
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        # Behind proxy
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        # Behind nginx
        return request.environ.get('HTTP_X_REAL_IP')
    else:
        # Direct connection
        return request.environ.get('REMOTE_ADDR')


def get_user_agent():
    """Get user agent from request"""
    return request.headers.get('User-Agent', '')[:500]  # Limit length


def log_user_action(action, resource=None, resource_id=None, details=None, success=True, error_message=None):
    """Log current user action"""
    from app.models import AuditLog
    
    user = None
    admin = None
    
    if current_user.is_authenticated:
        if isinstance(current_user._get_current_object(), AdminUser):
            admin = current_user._get_current_object()
        else:
            user = current_user._get_current_object()
    
    return AuditLog.log(
        action=action,
        user=user,
        admin=admin,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=get_client_ip(),
        user_agent=get_user_agent(),
        success=success,
        error_message=error_message
    )