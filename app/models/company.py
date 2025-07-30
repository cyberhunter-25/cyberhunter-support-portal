"""
Company model for multi-tenant support
"""
from datetime import datetime
from app.extensions import db


class Company(db.Model):
    """Company model for client organizations"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    domain = db.Column(db.String(255), nullable=False, index=True)
    contact_info = db.Column(db.JSON, nullable=True)  # {email, phone, address}
    active = db.Column(db.Boolean, default=True, nullable=False)
    allow_local_auth = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', back_populates='company', lazy='dynamic')
    tickets = db.relationship('Ticket', back_populates='company', lazy='dynamic')
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'contact_info': self.contact_info,
            'active': self.active,
            'allow_local_auth': self.allow_local_auth,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_count': self.users.count(),
            'ticket_count': self.tickets.count()
        }
    
    @property
    def active_users(self):
        """Get active users for this company"""
        return self.users.filter_by(active=True)
    
    @property
    def open_tickets(self):
        """Get open tickets for this company"""
        return self.tickets.filter(Ticket.status.in_(['new', 'in_progress', 'pending_client_response']))
    
    def is_domain_allowed(self, email):
        """Check if email domain matches company domain"""
        if not email or '@' not in email:
            return False
        email_domain = email.split('@')[1].lower()
        company_domains = [d.strip().lower() for d in self.domain.split(',')]
        return email_domain in company_domains