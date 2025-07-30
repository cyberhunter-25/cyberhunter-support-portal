"""
Admin user model with mandatory MFA
"""
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import pyotp

from app.extensions import db


class AdminUser(UserMixin, db.Model):
    """Admin user model with enhanced security"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role
    role = db.Column(db.Enum('admin', 'support', name='admin_role'), nullable=False, default='support')
    
    # MFA (mandatory for admins)
    mfa_secret = db.Column(db.String(32), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=False, nullable=False)
    backup_codes = db.Column(db.JSON, nullable=True)
    
    # Security
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_reset_token = db.Column(db.String(100), nullable=True, unique=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Status
    active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'
    
    def get_id(self):
        """Override Flask-Login's get_id to prefix with 'admin_'"""
        return f'admin_{self.id}'
    
    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    @property
    def is_support(self):
        """Check if user has support role"""
        return self.role == 'support'
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """Check if account is locked"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def increment_failed_attempts(self, lockout_attempts=5, lockout_duration=1800):
        """Increment failed login attempts"""
        self.failed_attempts += 1
        if self.failed_attempts >= lockout_attempts:
            self.locked_until = datetime.utcnow() + timedelta(seconds=lockout_duration)
        db.session.commit()
    
    def reset_failed_attempts(self):
        """Reset failed attempts on successful login"""
        self.failed_attempts = 0
        self.locked_until = None
        db.session.commit()
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def generate_reset_token(self):
        """Generate password reset token"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return self.password_reset_token
    
    def verify_reset_token(self, token):
        """Verify password reset token"""
        if not self.password_reset_token or self.password_reset_token != token:
            return False
        if not self.token_expiry or self.token_expiry < datetime.utcnow():
            return False
        return True
    
    def clear_reset_token(self):
        """Clear password reset token after use"""
        self.password_reset_token = None
        self.token_expiry = None
        db.session.commit()
    
    def setup_mfa(self):
        """Setup MFA with new secret"""
        self.mfa_secret = pyotp.random_base32()
        self.mfa_enabled = False  # Enable after verification
        return self.mfa_secret
    
    def get_totp_uri(self, issuer_name):
        """Get TOTP URI for QR code generation"""
        if not self.mfa_secret:
            return None
        return pyotp.totp.TOTP(self.mfa_secret).provisioning_uri(
            name=self.email,
            issuer_name=f"{issuer_name} Admin"
        )
    
    def verify_totp(self, token):
        """Verify TOTP token"""
        if not self.mfa_secret:
            return False
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.verify(token, valid_window=1)
    
    def enable_mfa(self):
        """Enable MFA after successful verification"""
        self.mfa_enabled = True
        db.session.commit()
    
    def disable_mfa(self):
        """Disable MFA (admin only)"""
        self.mfa_enabled = False
        self.mfa_secret = None
        self.backup_codes = None
        db.session.commit()
    
    def generate_backup_codes(self, count=10):
        """Generate backup codes for MFA"""
        codes = []
        hashed_codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            codes.append(f"{code[:4]}-{code[4:]}")
            hashed_codes.append(generate_password_hash(code))
        self.backup_codes = hashed_codes
        db.session.commit()
        return codes  # Return unhashed codes to show user once
    
    def verify_backup_code(self, code):
        """Verify and consume a backup code"""
        if not self.backup_codes:
            return False
        
        code = code.replace('-', '').upper()
        for i, hashed_code in enumerate(self.backup_codes):
            if check_password_hash(hashed_code, code):
                # Remove used code
                self.backup_codes.pop(i)
                db.session.commit()
                return True
        return False
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'mfa_enabled': self.mfa_enabled,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def find_by_username(cls, username):
        """Find admin by username"""
        return cls.query.filter_by(username=username.lower()).first()
    
    @classmethod
    def find_by_email(cls, email):
        """Find admin by email"""
        return cls.query.filter_by(email=email.lower()).first()