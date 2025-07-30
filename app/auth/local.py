"""
Local authentication handlers with MFA support
"""
import qrcode
import io
import base64
from datetime import datetime, timedelta
from flask import current_app, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import re

from app.extensions import db, limiter
from app.models import User, LocalAuth, Company, AdminUser, PasswordHistory
from app.utils import log_user_action, get_client_ip, get_user_agent
from app.auth.mfa import generate_qr_code, verify_mfa_token


class LoginForm(FlaskForm):
    """Login form for local authentication"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Registration form for local users"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20),
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=12)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, field):
        """Validate username is unique"""
        if LocalAuth.query.filter_by(username=field.data.lower()).first():
            raise ValidationError('Username already exists')
    
    def validate_email(self, field):
        """Validate email is unique and allowed"""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered')
    
    def validate_password(self, field):
        """Validate password complexity"""
        password = field.data
        
        if current_app.config.get('PASSWORD_REQUIRE_UPPERCASE') and not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        if current_app.config.get('PASSWORD_REQUIRE_LOWERCASE') and not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        if current_app.config.get('PASSWORD_REQUIRE_NUMBERS') and not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number')
        
        if current_app.config.get('PASSWORD_REQUIRE_SPECIAL') and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character')


class MFASetupForm(FlaskForm):
    """MFA setup form"""
    token = StringField('Verification Code', validators=[
        DataRequired(),
        Length(min=6, max=6)
    ])
    submit = SubmitField('Verify and Enable MFA')


class MFAVerifyForm(FlaskForm):
    """MFA verification form"""
    token = StringField('Authentication Code', validators=[
        DataRequired(),
        Length(min=6, max=6)
    ])
    submit = SubmitField('Verify')


class PasswordResetRequestForm(FlaskForm):
    """Password reset request form"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    submit = SubmitField('Request Password Reset')


class PasswordResetForm(FlaskForm):
    """Password reset form"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=12)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')


def init_local_auth_routes(bp):
    """Initialize local authentication routes"""
    
    @bp.route('/login', methods=['GET', 'POST'])
    @limiter.limit("5 per minute")
    def login():
        """Local user login"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data.lower()
            password = form.password.data
            
            # Find user by username or email
            local_auth = LocalAuth.query.filter_by(username=username).first()
            if not local_auth:
                # Try email
                user = User.query.filter_by(email=username, auth_type='local').first()
                if user:
                    local_auth = user.local_auth
            
            if not local_auth:
                flash('Invalid username or password', 'error')
                log_user_action(
                    action='local_login_failed',
                    details={'username': username, 'reason': 'user_not_found'},
                    success=False
                )
                return redirect(url_for('auth.login'))
            
            # Check if account is locked
            if local_auth.is_locked():
                flash('Account is locked due to too many failed attempts. Please try again later.', 'error')
                log_user_action(
                    action='local_login_blocked',
                    user=local_auth.user,
                    details={'reason': 'account_locked'},
                    success=False
                )
                return redirect(url_for('auth.login'))
            
            # Verify password
            if not local_auth.check_password(password):
                local_auth.increment_failed_attempts(
                    current_app.config['ACCOUNT_LOCKOUT_ATTEMPTS'],
                    current_app.config['ACCOUNT_LOCKOUT_DURATION']
                )
                flash('Invalid username or password', 'error')
                log_user_action(
                    action='local_login_failed',
                    user=local_auth.user,
                    details={'reason': 'invalid_password'},
                    success=False
                )
                return redirect(url_for('auth.login'))
            
            # Check if user is active
            if not local_auth.user.active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                log_user_action(
                    action='local_login_blocked',
                    user=local_auth.user,
                    details={'reason': 'account_deactivated'},
                    success=False
                )
                return redirect(url_for('auth.login'))
            
            # Reset failed attempts
            local_auth.reset_failed_attempts()
            
            # Check if MFA is enabled
            if local_auth.mfa_enabled:
                # Store user ID in session for MFA verification
                session['pending_user_id'] = local_auth.user.id
                session['remember_me'] = form.remember_me.data
                return redirect(url_for('auth.verify_mfa'))
            
            # Login successful
            login_user(local_auth.user, remember=form.remember_me.data)
            local_auth.user.update_last_login()
            
            log_user_action(
                action='local_login_success',
                user=local_auth.user
            )
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('tickets.index'))
        
        return render_template('auth/login.html', form=form)
    
    @bp.route('/register', methods=['GET', 'POST'])
    def register():
        """Register new local user"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if not current_app.config.get('LOCAL_AUTH_ENABLED'):
            flash('Local registration is disabled', 'error')
            return redirect(url_for('auth.login'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            email = form.email.data.lower()
            
            # Find company by email domain
            company = find_company_by_email(email)
            if not company:
                flash('Your email domain is not authorized. Please contact your administrator.', 'error')
                return redirect(url_for('auth.register'))
            
            if not company.allow_local_auth:
                flash('Local authentication is not enabled for your company. Please use OAuth login.', 'error')
                return redirect(url_for('auth.login'))
            
            # Create user
            user = User(
                company_id=company.id,
                email=email,
                name=form.name.data,
                auth_type='local',
                active=True,
                email_verified=False  # Will need email verification
            )
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create local auth
            local_auth = LocalAuth(
                user_id=user.id,
                username=form.username.data.lower()
            )
            local_auth.set_password(form.password.data)
            db.session.add(local_auth)
            
            # Add to password history
            PasswordHistory.add_password(local_auth.id, local_auth.password_hash)
            
            db.session.commit()
            
            flash('Registration successful! Please check your email to verify your account.', 'success')
            log_user_action(
                action='local_user_registered',
                user=user
            )
            
            # TODO: Send verification email
            
            return redirect(url_for('auth.login'))
        
        return render_template('auth/register.html', form=form)
    
    @bp.route('/verify-mfa', methods=['GET', 'POST'])
    def verify_mfa():
        """Verify MFA token"""
        pending_user_id = session.get('pending_user_id')
        if not pending_user_id:
            return redirect(url_for('auth.login'))
        
        user = User.query.get(pending_user_id)
        if not user or not user.local_auth:
            session.pop('pending_user_id', None)
            return redirect(url_for('auth.login'))
        
        form = MFAVerifyForm()
        if form.validate_on_submit():
            token = form.token.data.replace(' ', '')
            
            if user.local_auth.verify_totp(token):
                # MFA successful
                remember_me = session.pop('remember_me', False)
                session.pop('pending_user_id', None)
                session['mfa_verified'] = True
                
                login_user(user, remember=remember_me)
                user.update_last_login()
                
                log_user_action(
                    action='mfa_verification_success',
                    user=user
                )
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('tickets.index'))
            else:
                # Check backup codes
                if user.local_auth.verify_backup_code(token):
                    remember_me = session.pop('remember_me', False)
                    session.pop('pending_user_id', None)
                    session['mfa_verified'] = True
                    
                    login_user(user, remember=remember_me)
                    user.update_last_login()
                    
                    flash('Backup code used successfully. Please generate new backup codes.', 'warning')
                    log_user_action(
                        action='mfa_backup_code_used',
                        user=user
                    )
                    
                    return redirect(url_for('tickets.index'))
                else:
                    flash('Invalid authentication code', 'error')
                    log_user_action(
                        action='mfa_verification_failed',
                        user=user,
                        success=False
                    )
        
        return render_template('auth/mfa_verify.html', form=form)
    
    @bp.route('/setup-mfa', methods=['GET', 'POST'])
    def setup_mfa():
        """Setup MFA for user"""
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not hasattr(current_user, 'local_auth') or not current_user.local_auth:
            flash('MFA is only available for local authentication', 'error')
            return redirect(url_for('index'))
        
        if current_user.local_auth.mfa_enabled:
            flash('MFA is already enabled for your account', 'info')
            return redirect(url_for('index'))
        
        form = MFASetupForm()
        
        # Generate or retrieve secret
        if not current_user.local_auth.mfa_secret:
            current_user.local_auth.setup_mfa()
            db.session.commit()
        
        if form.validate_on_submit():
            token = form.token.data.replace(' ', '')
            
            if current_user.local_auth.verify_totp(token):
                # Enable MFA
                current_user.local_auth.enable_mfa()
                
                # Generate backup codes
                backup_codes = current_user.local_auth.generate_backup_codes()
                
                log_user_action(
                    action='mfa_enabled',
                    user=current_user._get_current_object()
                )
                
                return render_template('auth/mfa_backup_codes.html', backup_codes=backup_codes)
            else:
                flash('Invalid verification code. Please try again.', 'error')
        
        # Generate QR code
        qr_uri = current_user.local_auth.get_totp_uri(current_app.config['MFA_ISSUER_NAME'])
        qr_code = generate_qr_code(qr_uri)
        
        return render_template('auth/mfa_setup.html', form=form, qr_code=qr_code, secret=current_user.local_auth.mfa_secret)


def find_company_by_email(email):
    """Find company by email domain"""
    if not email or '@' not in email:
        return None
    
    domain = email.split('@')[1].lower()
    
    # Find all active companies
    companies = Company.query.filter_by(active=True).all()
    
    for company in companies:
        if company.is_domain_allowed(email):
            return company
    
    return None