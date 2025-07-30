"""
Authentication routes combining OAuth and local auth
"""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

from app.auth import auth_bp
from app.auth.oauth import init_oauth_routes
from app.auth.local import init_local_auth_routes, LoginForm
from app.models import AdminUser
from app.utils import log_user_action
from app.extensions import limiter, db


class AdminLoginForm(FlaskForm):
    """Admin login form"""
    username = PasswordField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


# Initialize OAuth routes
init_oauth_routes(auth_bp)

# Initialize local auth routes
init_local_auth_routes(auth_bp)


@auth_bp.route('/logout')
def logout():
    """Logout current user"""
    if current_user.is_authenticated:
        user = current_user._get_current_object()
        
        # Determine user type for logging
        if isinstance(user, AdminUser):
            log_user_action(action='logout', admin=user)
        else:
            log_user_action(action='logout', user=user)
        
        logout_user()
        session.clear()  # Clear all session data
        flash('You have been logged out.', 'info')
    
    return redirect(url_for('index'))


@auth_bp.route('/admin-login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated:
        if isinstance(current_user._get_current_object(), AdminUser):
            return redirect(url_for('admin.dashboard'))
        else:
            logout_user()  # Logout regular user
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data
        
        # Find admin by username
        admin = AdminUser.find_by_username(username)
        
        if not admin:
            flash('Invalid username or password', 'error')
            log_user_action(
                action='admin_login_failed',
                details={'username': username, 'reason': 'user_not_found'},
                success=False
            )
            return redirect(url_for('auth.admin_login'))
        
        # Check if account is locked
        if admin.is_locked():
            flash('Account is locked due to too many failed attempts. Please try again later.', 'error')
            log_user_action(
                action='admin_login_blocked',
                admin=admin,
                details={'reason': 'account_locked'},
                success=False
            )
            return redirect(url_for('auth.admin_login'))
        
        # Verify password
        if not admin.check_password(password):
            admin.increment_failed_attempts()
            flash('Invalid username or password', 'error')
            log_user_action(
                action='admin_login_failed',
                admin=admin,
                details={'reason': 'invalid_password'},
                success=False
            )
            return redirect(url_for('auth.admin_login'))
        
        # Check if admin is active
        if not admin.active:
            flash('Your account has been deactivated.', 'error')
            log_user_action(
                action='admin_login_blocked',
                admin=admin,
                details={'reason': 'account_deactivated'},
                success=False
            )
            return redirect(url_for('auth.admin_login'))
        
        # Reset failed attempts
        admin.reset_failed_attempts()
        
        # Store admin ID in session for MFA verification
        session['pending_admin_id'] = admin.id
        return redirect(url_for('auth.admin_verify_mfa'))
    
    return render_template('auth/admin_login.html', form=form)


@auth_bp.route('/admin/verify-mfa', methods=['GET', 'POST'])
def admin_verify_mfa():
    """Admin MFA verification"""
    from app.auth.local import MFAVerifyForm
    
    pending_admin_id = session.get('pending_admin_id')
    if not pending_admin_id:
        return redirect(url_for('auth.admin_login'))
    
    admin = AdminUser.query.get(pending_admin_id)
    if not admin:
        session.pop('pending_admin_id', None)
        return redirect(url_for('auth.admin_login'))
    
    # Check if MFA is set up
    if not admin.mfa_secret:
        # First time login - require MFA setup
        return redirect(url_for('auth.admin_setup_mfa'))
    
    form = MFAVerifyForm()
    if form.validate_on_submit():
        token = form.token.data.replace(' ', '')
        
        if admin.verify_totp(token):
            # MFA successful
            session.pop('pending_admin_id', None)
            session['mfa_verified'] = True
            
            login_user(admin, remember=False)  # Never remember admin sessions
            admin.update_last_login()
            
            log_user_action(
                action='admin_login_success',
                admin=admin
            )
            
            flash(f'Welcome back, {admin.username}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            # Check backup codes
            if admin.verify_backup_code(token):
                session.pop('pending_admin_id', None)
                session['mfa_verified'] = True
                
                login_user(admin, remember=False)
                admin.update_last_login()
                
                flash('Backup code used successfully. Please generate new backup codes.', 'warning')
                log_user_action(
                    action='admin_mfa_backup_code_used',
                    admin=admin
                )
                
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid authentication code', 'error')
                log_user_action(
                    action='admin_mfa_verification_failed',
                    admin=admin,
                    success=False
                )
    
    return render_template('auth/admin_mfa_verify.html', form=form)


@auth_bp.route('/admin/setup-mfa', methods=['GET', 'POST'])
def admin_setup_mfa():
    """Admin MFA setup (first time)"""
    from app.auth.local import MFASetupForm
    from app.auth.mfa import generate_qr_code
    
    pending_admin_id = session.get('pending_admin_id')
    if not pending_admin_id:
        return redirect(url_for('auth.admin_login'))
    
    admin = AdminUser.query.get(pending_admin_id)
    if not admin:
        session.pop('pending_admin_id', None)
        return redirect(url_for('auth.admin_login'))
    
    form = MFASetupForm()
    
    # Generate or retrieve secret
    if not admin.mfa_secret:
        admin.setup_mfa()
        db.session.commit()
    
    if form.validate_on_submit():
        token = form.token.data.replace(' ', '')
        
        if admin.verify_totp(token):
            # Enable MFA
            admin.enable_mfa()
            
            # Generate backup codes
            backup_codes = admin.generate_backup_codes()
            
            # Login admin
            session.pop('pending_admin_id', None)
            session['mfa_verified'] = True
            login_user(admin, remember=False)
            admin.update_last_login()
            
            log_user_action(
                action='admin_mfa_enabled',
                admin=admin
            )
            
            return render_template('auth/admin_mfa_backup_codes.html', backup_codes=backup_codes)
        else:
            flash('Invalid verification code. Please try again.', 'error')
    
    # Generate QR code
    qr_uri = admin.get_totp_uri(current_app.config['MFA_ISSUER_NAME'])
    qr_code = generate_qr_code(qr_uri)
    
    return render_template('auth/admin_mfa_setup.html', form=form, qr_code=qr_code, secret=admin.mfa_secret)


@auth_bp.route('/password-reset', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def password_reset_request():
    """Request password reset"""
    from app.auth.local import PasswordResetRequestForm
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter_by(email=email, auth_type='local').first()
        
        if user and user.local_auth:
            # Generate reset token
            token = user.local_auth.generate_reset_token()
            
            # TODO: Send reset email
            # For now, just flash the link (remove in production)
            reset_url = url_for('auth.password_reset', token=token, _external=True)
            flash(f'Password reset link: {reset_url}', 'info')  # REMOVE IN PRODUCTION
            
            log_user_action(
                action='password_reset_requested',
                user=user
            )
        
        # Always show success message to prevent email enumeration
        flash('If your email is registered, you will receive a password reset link.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/password_reset_request.html', form=form)


@auth_bp.route('/password-reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """Reset password with token"""
    from app.auth.local import PasswordResetForm
    from app.models import User
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Find user by token
    local_auth = LocalAuth.query.filter_by(password_reset_token=token).first()
    
    if not local_auth or not local_auth.verify_reset_token(token):
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('auth.login'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Check password history
        if PasswordHistory.check_password_reuse(
            local_auth.id, 
            form.password.data,
            current_app.config['PASSWORD_HISTORY_COUNT']
        ):
            flash(f'Password has been used recently. Please choose a different password.', 'error')
            return redirect(url_for('auth.password_reset', token=token))
        
        # Set new password
        local_auth.set_password(form.password.data)
        local_auth.clear_reset_token()
        
        # Add to password history
        PasswordHistory.add_password(local_auth.id, local_auth.password_hash)
        
        db.session.commit()
        
        flash('Your password has been reset. You can now log in.', 'success')
        log_user_action(
            action='password_reset_completed',
            user=local_auth.user
        )
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/password_reset.html', form=form)