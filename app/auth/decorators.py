"""
Authentication decorators
"""
from functools import wraps
from flask import redirect, url_for, flash, abort, request
from flask_login import current_user
from app.models import AdminUser


def login_required(f):
    """Custom login required decorator that handles both user types"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.admin_login', next=request.url))
        
        # Check if current user is an admin
        if not isinstance(current_user._get_current_object(), AdminUser):
            abort(403)
        
        if not current_user.active:
            flash('Your account has been deactivated.', 'error')
            return redirect(url_for('auth.logout'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_role_required(role):
    """Require specific admin role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'info')
                return redirect(url_for('auth.admin_login', next=request.url))
            
            # Check if current user is an admin
            if not isinstance(current_user._get_current_object(), AdminUser):
                abort(403)
            
            if current_user.role != role:
                flash(f'You need {role} privileges to access this page.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def company_access_required(f):
    """Ensure user can only access their company's resources"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Admins can access all companies
        if isinstance(current_user._get_current_object(), AdminUser):
            return f(*args, **kwargs)
        
        # Regular users can only access their company's data
        # This will be implemented when checking specific resources
        return f(*args, **kwargs)
    return decorated_function


def mfa_required(f):
    """Require MFA verification for sensitive operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Check if user has MFA enabled and verified in this session
        if hasattr(current_user, 'mfa_enabled') and current_user.mfa_enabled:
            # Check session for MFA verification
            from flask import session
            if not session.get('mfa_verified'):
                flash('Please verify your MFA to continue.', 'warning')
                return redirect(url_for('auth.verify_mfa', next=request.url))
        
        return f(*args, **kwargs)
    return decorated_function