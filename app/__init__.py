"""
Flask Application Factory for CyberHunter Security Portal
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_login import current_user

from app.config import config
from app.extensions import init_extensions, db
from app.utils import load_user  # Import to register user loader


def create_app(config_name=None):
    """Create and configure Flask application"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup logging
    setup_logging(app)
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Shell context for development
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': None,  # Will be imported when models are created
        }
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    return app


def register_blueprints(app):
    """Register all blueprints"""
    from app.auth import auth_bp
    from app.tickets import tickets_bp
    from app.admin import admin_bp
    from app.api.v1 import api_v1_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    
    # Main routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return render_template('index.html')
        return render_template('landing.html')


def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_error(error):
        return render_template('errors/429.html'), 429


def setup_logging(app):
    """Setup application logging"""
    if not app.debug and not app.testing:
        # Create logs directory
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Application log
        file_handler = RotatingFileHandler(
            'logs/cyberhunter_portal.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Audit log
        audit_handler = RotatingFileHandler(
            'logs/audit.log',
            maxBytes=10485760,
            backupCount=30
        )
        audit_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(message)s'
        ))
        audit_logger = logging.getLogger('audit')
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('CyberHunter Security Portal startup')