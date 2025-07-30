"""
Audit log model for security tracking
"""
from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    """Audit log for tracking all system actions"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True, index=True)
    user_type = db.Column(db.Enum('user', 'admin', 'system', name='audit_user_type'), nullable=False)
    
    # Action details
    action = db.Column(db.String(100), nullable=False, index=True)
    resource = db.Column(db.String(100), nullable=True)
    resource_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    
    # Request information
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 support
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Result
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', back_populates='audit_logs')
    admin = db.relationship('AdminUser', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_type} at {self.created_at}>'
    
    @classmethod
    def log(cls, action, user=None, admin=None, resource=None, resource_id=None, 
            details=None, ip_address=None, user_agent=None, success=True, error_message=None):
        """Create audit log entry"""
        # Determine user type
        if admin:
            user_type = 'admin'
            admin_id = admin.id
            user_id = None
        elif user:
            user_type = 'user'
            user_id = user.id
            admin_id = None
        else:
            user_type = 'system'
            user_id = None
            admin_id = None
        
        log_entry = cls(
            user_id=user_id,
            admin_id=admin_id,
            user_type=user_type,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @classmethod
    def log_login(cls, user=None, admin=None, success=True, ip_address=None, user_agent=None, error=None):
        """Log login attempt"""
        return cls.log(
            action='login',
            user=user,
            admin=admin,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error
        )
    
    @classmethod
    def log_logout(cls, user=None, admin=None, ip_address=None, user_agent=None):
        """Log logout"""
        return cls.log(
            action='logout',
            user=user,
            admin=admin,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @classmethod
    def log_ticket_action(cls, action, ticket, user=None, admin=None, details=None, ip_address=None, user_agent=None):
        """Log ticket-related action"""
        return cls.log(
            action=f'ticket_{action}',
            user=user,
            admin=admin,
            resource='ticket',
            resource_id=ticket.id,
            details={'ticket_number': ticket.ticket_number, **(details or {})},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @classmethod
    def log_security_event(cls, event, details, ip_address=None, user_agent=None, user=None, admin=None):
        """Log security event"""
        return cls.log(
            action=f'security_{event}',
            user=user,
            admin=admin,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False
        )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_type': self.user_type,
            'user': self.user.email if self.user else None,
            'admin': self.admin.username if self.admin else None,
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }