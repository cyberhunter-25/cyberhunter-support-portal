"""
System Settings Model
"""
from app.extensions import db
from sqlalchemy import Column, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from cryptography.fernet import Fernet
import os


class SystemSettings(db.Model):
    """
    System configuration settings stored in database
    """
    __tablename__ = 'system_settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(Text)
    encrypted = Column(Boolean, default=False)
    description = Column(String(500))
    category = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            return setting.get_value()
        return default
    
    @classmethod
    def set_setting(cls, key, value, encrypted=False, description=None, category=None):
        """Set or update a setting"""
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(key=key)
            db.session.add(setting)
        
        setting.set_value(value, encrypted)
        if description:
            setting.description = description
        if category:
            setting.category = category
        
        db.session.commit()
        return setting
    
    def get_value(self):
        """Get the decrypted value"""
        if self.encrypted and self.value:
            try:
                key = self._get_encryption_key()
                f = Fernet(key)
                return f.decrypt(self.value.encode()).decode()
            except Exception:
                return None
        return self.value
    
    def set_value(self, value, encrypted=False):
        """Set the value, encrypting if needed"""
        if encrypted and value:
            key = self._get_encryption_key()
            f = Fernet(key)
            self.value = f.encrypt(value.encode()).decode()
            self.encrypted = True
        else:
            self.value = value
            self.encrypted = False
    
    def _get_encryption_key(self):
        """Get or create encryption key"""
        key = os.environ.get('SETTINGS_ENCRYPTION_KEY')
        if not key:
            # Generate a new key if not set
            key = Fernet.generate_key().decode()
            # In production, this should be set in environment variables
            os.environ['SETTINGS_ENCRYPTION_KEY'] = key
        return key.encode() if isinstance(key, str) else key
    
    @classmethod
    def get_oauth_settings(cls):
        """Get all OAuth settings"""
        return {
            'microsoft_client_id': cls.get_setting('oauth.microsoft.client_id', ''),
            'microsoft_client_secret': cls.get_setting('oauth.microsoft.client_secret', ''),
            'microsoft_tenant_id': cls.get_setting('oauth.microsoft.tenant_id', 'common'),
            'google_client_id': cls.get_setting('oauth.google.client_id', ''),
            'google_client_secret': cls.get_setting('oauth.google.client_secret', ''),
            'allowed_domains': cls.get_setting('oauth.allowed_domains', '').split(',') if cls.get_setting('oauth.allowed_domains') else []
        }
    
    @classmethod
    def set_oauth_settings(cls, settings):
        """Set OAuth settings"""
        cls.set_setting('oauth.microsoft.client_id', settings.get('microsoft_client_id', ''), 
                       description='Microsoft OAuth Client ID', category='oauth')
        cls.set_setting('oauth.microsoft.client_secret', settings.get('microsoft_client_secret', ''), 
                       encrypted=True, description='Microsoft OAuth Client Secret', category='oauth')
        cls.set_setting('oauth.microsoft.tenant_id', settings.get('microsoft_tenant_id', 'common'), 
                       description='Microsoft OAuth Tenant ID', category='oauth')
        cls.set_setting('oauth.google.client_id', settings.get('google_client_id', ''), 
                       description='Google OAuth Client ID', category='oauth')
        cls.set_setting('oauth.google.client_secret', settings.get('google_client_secret', ''), 
                       encrypted=True, description='Google OAuth Client Secret', category='oauth')
        cls.set_setting('oauth.allowed_domains', ','.join(settings.get('allowed_domains', [])), 
                       description='Comma-separated list of allowed email domains', category='oauth')
    
    @classmethod
    def get_email_settings(cls):
        """Get all email settings"""
        return {
            'smtp_server': cls.get_setting('email.smtp.server', 'smtp.gmail.com'),
            'smtp_port': int(cls.get_setting('email.smtp.port', '587')),
            'smtp_username': cls.get_setting('email.smtp.username', ''),
            'smtp_password': cls.get_setting('email.smtp.password', ''),
            'smtp_use_tls': cls.get_setting('email.smtp.use_tls', 'true').lower() == 'true',
            'from_address': cls.get_setting('email.from_address', 'guardian@clirsec.com'),
            'from_name': cls.get_setting('email.from_name', 'CyberHunter Support'),
            'imap_server': cls.get_setting('email.imap.server', 'imap.gmail.com'),
            'imap_port': int(cls.get_setting('email.imap.port', '993')),
            'imap_username': cls.get_setting('email.imap.username', ''),
            'imap_password': cls.get_setting('email.imap.password', ''),
            'imap_use_ssl': cls.get_setting('email.imap.use_ssl', 'true').lower() == 'true'
        }
    
    @classmethod
    def set_email_settings(cls, settings):
        """Set email settings"""
        cls.set_setting('email.smtp.server', settings.get('smtp_server', 'smtp.gmail.com'), 
                       description='SMTP Server Address', category='email')
        cls.set_setting('email.smtp.port', str(settings.get('smtp_port', 587)), 
                       description='SMTP Server Port', category='email')
        cls.set_setting('email.smtp.username', settings.get('smtp_username', ''), 
                       description='SMTP Username', category='email')
        cls.set_setting('email.smtp.password', settings.get('smtp_password', ''), 
                       encrypted=True, description='SMTP Password', category='email')
        cls.set_setting('email.smtp.use_tls', str(settings.get('smtp_use_tls', True)).lower(), 
                       description='Use TLS for SMTP', category='email')
        cls.set_setting('email.from_address', settings.get('from_address', 'guardian@clirsec.com'), 
                       description='From Email Address', category='email')
        cls.set_setting('email.from_name', settings.get('from_name', 'CyberHunter Support'), 
                       description='From Name', category='email')
        cls.set_setting('email.imap.server', settings.get('imap_server', 'imap.gmail.com'), 
                       description='IMAP Server Address', category='email')
        cls.set_setting('email.imap.port', str(settings.get('imap_port', 993)), 
                       description='IMAP Server Port', category='email')
        cls.set_setting('email.imap.username', settings.get('imap_username', ''), 
                       description='IMAP Username', category='email')
        cls.set_setting('email.imap.password', settings.get('imap_password', ''), 
                       encrypted=True, description='IMAP Password', category='email')
        cls.set_setting('email.imap.use_ssl', str(settings.get('imap_use_ssl', True)).lower(), 
                       description='Use SSL for IMAP', category='email')
    
    def __repr__(self):
        return f'<SystemSettings {self.key}: {self.value[:50] if self.value else None}>'