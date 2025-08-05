"""
Flask extensions initialization
"""
import redis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth
from celery import Celery

# Database
db = SQLAlchemy()
migrate = Migrate()

# Authentication
login_manager = LoginManager()
oauth = OAuth()

# Email
mail = Mail()

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Caching
cache = Cache()

# Session
sess = Session()

# CSRF Protection
csrf = CSRFProtect()

# Celery
celery = Celery()


def init_extensions(app):
    """Initialize all Flask extensions"""
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Authentication
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # OAuth
    oauth.init_app(app)
    
    # Configure OAuth providers
    if app.config.get('MICROSOFT_CLIENT_ID'):
        oauth.register(
            name='microsoft',
            client_id=app.config['MICROSOFT_CLIENT_ID'],
            client_secret=app.config['MICROSOFT_CLIENT_SECRET'],
            server_metadata_url=f'https://login.microsoftonline.com/{app.config["MICROSOFT_TENANT_ID"]}/v2.0/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile User.Read'
            }
        )
    
    if app.config.get('GOOGLE_CLIENT_ID'):
        oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
    
    # Email
    mail.init_app(app)
    
    # Rate limiting
    if app.config.get('RATELIMIT_ENABLED'):
        limiter._storage_uri = app.config.get('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/3')
        limiter.init_app(app)
    else:
        # Initialize limiter without storage to avoid Redis connection
        limiter.enabled = False
        limiter.init_app(app)
    
    # Caching
    cache.init_app(app, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    })
    
    # Session - Configure Redis connection from SESSION_REDIS_URL
    redis_url = app.config.get('SESSION_REDIS_URL', 'redis://localhost:6379/2')
    # Parse the Redis URL to create a Redis instance
    if redis_url.startswith('redis://'):
        # Extract password if present
        if '@' in redis_url:
            # Format: redis://:password@host:port/db
            parts = redis_url.replace('redis://', '').split('@')
            auth_part = parts[0]
            host_part = parts[1]
            
            password = None
            if auth_part.startswith(':'):
                password = auth_part[1:]
            
            host, port_db = host_part.split(':')
            port, db_num = port_db.split('/')
            
            app.config['SESSION_REDIS'] = redis.Redis(
                host=host,
                port=int(port),
                db=int(db_num),
                password=password,
                decode_responses=False
            )
        else:
            # Format: redis://host:port/db
            host_part = redis_url.replace('redis://', '')
            host, port_db = host_part.split(':')
            port, db_num = port_db.split('/')
            
            app.config['SESSION_REDIS'] = redis.Redis(
                host=host,
                port=int(port),
                db=int(db_num),
                decode_responses=False
            )
    
    sess.init_app(app)
    
    # CSRF
    csrf.init_app(app)
    
    # Celery
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    # Update celery config with Flask app config
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    return None