"""
Configuration classes for CyberHunter Security Portal
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost/cyberhunter_portal'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Session
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_NAME = 'cyberhunter_session'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # OAuth - Microsoft
    MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID')
    MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET')
    MICROSOFT_TENANT_ID = os.environ.get('MICROSOFT_TENANT_ID', 'common')
    
    # OAuth - Google
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Local Authentication
    LOCAL_AUTH_ENABLED = os.environ.get('LOCAL_AUTH_ENABLED', 'True').lower() == 'true'
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 12))
    PASSWORD_REQUIRE_UPPERCASE = os.environ.get('PASSWORD_REQUIRE_UPPERCASE', 'True').lower() == 'true'
    PASSWORD_REQUIRE_LOWERCASE = os.environ.get('PASSWORD_REQUIRE_LOWERCASE', 'True').lower() == 'true'
    PASSWORD_REQUIRE_NUMBERS = os.environ.get('PASSWORD_REQUIRE_NUMBERS', 'True').lower() == 'true'
    PASSWORD_REQUIRE_SPECIAL = os.environ.get('PASSWORD_REQUIRE_SPECIAL', 'True').lower() == 'true'
    PASSWORD_HISTORY_COUNT = int(os.environ.get('PASSWORD_HISTORY_COUNT', 5))
    ACCOUNT_LOCKOUT_ATTEMPTS = int(os.environ.get('ACCOUNT_LOCKOUT_ATTEMPTS', 5))
    ACCOUNT_LOCKOUT_DURATION = int(os.environ.get('ACCOUNT_LOCKOUT_DURATION', 1800))  # 30 minutes
    
    # MFA
    MFA_ISSUER_NAME = os.environ.get('MFA_ISSUER_NAME', 'CyberHunter Security Portal')
    MFA_BACKUP_CODES_COUNT = int(os.environ.get('MFA_BACKUP_CODES_COUNT', 10))
    ADMIN_MFA_REQUIRED = os.environ.get('ADMIN_MFA_REQUIRED', 'True').lower() == 'true'
    
    # Email
    MAIL_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('SMTP_PORT', 587))
    MAIL_USE_TLS = os.environ.get('SMTP_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('SMTP_USERNAME')
    MAIL_PASSWORD = os.environ.get('SMTP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('SMTP_DEFAULT_SENDER', 'CyberHunter Support <guardian@clirsec.com>')
    
    # IMAP
    IMAP_SERVER = os.environ.get('IMAP_SERVER', 'imap.gmail.com')
    IMAP_PORT = int(os.environ.get('IMAP_PORT', 993))
    IMAP_USE_SSL = os.environ.get('IMAP_USE_SSL', 'True').lower() == 'true'
    IMAP_USERNAME = os.environ.get('IMAP_USERNAME')
    IMAP_PASSWORD = os.environ.get('IMAP_PASSWORD')
    IMAP_POLL_INTERVAL = int(os.environ.get('IMAP_POLL_INTERVAL', 60))
    
    # File Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/cyberhunter-uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 104857600))  # 100MB
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,pdf,doc,docx,txt,log,csv,zip,7z').split(','))
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 26214400))  # 25MB per file
    CLAMAV_ENABLED = os.environ.get('CLAMAV_ENABLED', 'True').lower() == 'true'
    CLAMAV_SOCKET = os.environ.get('CLAMAV_SOCKET', '/var/run/clamav/clamd.ctl')
    
    # Push Notifications
    NTFY_ENABLED = os.environ.get('NTFY_ENABLED', 'True').lower() == 'true'
    NTFY_SERVER = os.environ.get('NTFY_SERVER', 'https://ntfy.sh')
    NTFY_TOPIC = os.environ.get('NTFY_TOPIC', 'cyberhunter-alerts')
    NTFY_PRIORITY_THRESHOLD = int(os.environ.get('NTFY_PRIORITY_THRESHOLD', 2))
    
    # Application URLs
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'False').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'redis://redis:6379/3')
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100/hour')
    RATELIMIT_LOGIN = os.environ.get('RATELIMIT_LOGIN', '5/minute')
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    
    # Company
    COMPANY_NAME = os.environ.get('COMPANY_NAME', 'CyberHunter CLIRSec')
    SUPPORT_PHONE = os.environ.get('SUPPORT_PHONE', '+1-XXX-XXX-XXXX')
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'support@cyberhunter.com')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    # Less strict for development
    SESSION_COOKIE_SECURE = False
    PASSWORD_MIN_LENGTH = 8
    ACCOUNT_LOCKOUT_ATTEMPTS = 10


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # Enforce all security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Require strong passwords
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = True
    
    # Disable external services for testing
    CLAMAV_ENABLED = False
    NTFY_ENABLED = False
    RATELIMIT_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}