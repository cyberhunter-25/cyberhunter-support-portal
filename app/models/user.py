"""
User models supporting both OAuth and local authentication
"""
from datetime import datetime, timedelta
from flask_login import UserMixin
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import pyotp

from app.extensions import db


class User(UserMixin, db.Model):
    """User model supporting both OAuth and local authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    
    # Authentication type
    auth_type = db.Column(db.Enum('oauth', 'local', name='auth_type'), nullable=False)
    
    # OAuth fields (nullable for local auth users)
    oauth_provider = db.Column(db.Enum('microsoft', 'google', name='oauth_provider'), nullable=True)
    oauth_id = db.Column(db.String(255), nullable=True, index=True)
    
    # Status
    active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', back_populates='users')
    local_auth = db.relationship('LocalAuth', back_populates='user', uselist=False, cascade='all, delete-orphan')
    tickets = db.relationship('Ticket', back_populates='user', lazy='dynamic')
    messages = db.relationship('TicketMessage', back_populates='user', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', back_populates='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def is_local_auth(self):
        """Check if user uses local authentication"""
        return self.auth_type == 'local'
    
    @property
    def is_oauth_auth(self):
        """Check if user uses OAuth authentication"""
        return self.auth_type == 'oauth'
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'company': self.company.name,
            'auth_type': self.auth_type,
            'active': self.active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def find_by_oauth(cls, provider, oauth_id):
        """Find user by OAuth provider and ID"""
        return cls.query.filter_by(
            oauth_provider=provider,
            oauth_id=oauth_id,
            auth_type='oauth'
        ).first()
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        return cls.query.filter_by(email=email.lower()).first()


class LocalAuth(db.Model):
    """Local authentication data for users"""
    __tablename__ = 'local_auth'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # MFA
    mfa_secret = db.Column(db.String(32), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=False, nullable=False)
    backup_codes = db.Column(db.JSON, nullable=True)  # List of hashed backup codes
    
    # Password reset
    password_reset_token = db.Column(db.String(100), nullable=True, unique=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Security
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='local_auth')
    password_history = db.relationship('PasswordHistory', back_populates='local_auth', lazy='dynamic')
    
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
    
    def increment_failed_attempts(self, lockout_attempts, lockout_duration):
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
            name=self.user.email,
            issuer_name=issuer_name
        )
    
    def verify_totp(self, token):
        """Verify TOTP token"""
        if not self.mfa_secret:
            return False
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.verify(token, valid_window=1)
    
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


class PasswordHistory(db.Model):
    """Password history to prevent reuse"""
    __tablename__ = 'password_history'
    
    id = db.Column(db.Integer, primary_key=True)
    local_auth_id = db.Column(db.Integer, db.ForeignKey('local_auth.id'), nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    local_auth = db.relationship('LocalAuth', back_populates='password_history')
    
    @classmethod
    def check_password_reuse(cls, local_auth_id, password, history_count):
        """Check if password was recently used"""
        recent_passwords = cls.query.filter_by(local_auth_id=local_auth_id)\
            .order_by(cls.created_at.desc())\
            .limit(history_count)\
            .all()
        
        for history in recent_passwords:
            if check_password_hash(history.password_hash, password):
                return True
        return False
    
    @classmethod
    def add_password(cls, local_auth_id, password_hash):
        """Add password to history"""
        history = cls(
            local_auth_id=local_auth_id,
            password_hash=password_hash
        )
        db.session.add(history)
        db.session.commit()