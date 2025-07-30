"""
Ticket and message models
"""
from datetime import datetime
from app.extensions import db


class Ticket(db.Model):
    """Support ticket model"""
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), nullable=False, unique=True, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Ticket details
    priority = db.Column(db.Integer, nullable=False, index=True)  # 1-4
    status = db.Column(db.Enum(
        'new', 'in_progress', 'pending_client_response', 'resolved', 'closed',
        name='ticket_status'
    ), nullable=False, default='new', index=True)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    company = db.relationship('Company', back_populates='tickets')
    user = db.relationship('User', back_populates='tickets')
    messages = db.relationship('TicketMessage', back_populates='ticket', lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', back_populates='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ticket {self.ticket_number}>'
    
    @classmethod
    def generate_ticket_number(cls):
        """Generate unique ticket number: CH-YYYYMMDD-XXXX"""
        today = datetime.utcnow().strftime('%Y%m%d')
        
        # Get the last ticket number for today
        last_ticket = cls.query.filter(
            cls.ticket_number.like(f'CH-{today}-%')
        ).order_by(cls.id.desc()).first()
        
        if last_ticket:
            # Extract the sequence number and increment
            last_seq = int(last_ticket.ticket_number.split('-')[-1])
            next_seq = last_seq + 1
        else:
            next_seq = 1
        
        return f'CH-{today}-{next_seq:04d}'
    
    @property
    def priority_label(self):
        """Get priority label"""
        labels = {
            1: 'Critical Emergency',
            2: 'High',
            3: 'Medium',
            4: 'Low'
        }
        return labels.get(self.priority, 'Unknown')
    
    @property
    def sla_response_time(self):
        """Get SLA response time in minutes"""
        sla = {
            1: 15,      # 15 minutes
            2: 60,      # 1 hour
            3: 240,     # 4 hours
            4: 1440     # 1 business day
        }
        return sla.get(self.priority, 1440)
    
    def update_status(self, new_status):
        """Update ticket status with timestamps"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status == 'resolved':
            self.resolved_at = datetime.utcnow()
        elif new_status == 'closed':
            self.closed_at = datetime.utcnow()
        
        db.session.commit()
    
    def add_message(self, user, message, is_internal=False):
        """Add a message to the ticket"""
        msg = TicketMessage(
            ticket_id=self.id,
            user_id=user.id,
            message=message,
            is_internal=is_internal
        )
        db.session.add(msg)
        db.session.commit()
        return msg
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'ticket_number': self.ticket_number,
            'company': self.company.name,
            'user': {
                'name': self.user.name,
                'email': self.user.email
            },
            'priority': self.priority,
            'priority_label': self.priority_label,
            'status': self.status,
            'subject': self.subject,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'message_count': self.messages.count(),
            'attachment_count': self.attachments.count()
        }


class TicketMessage(db.Model):
    """Ticket communication messages"""
    __tablename__ = 'ticket_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    
    # Message content
    message = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False, nullable=False)  # Internal notes
    
    # Email tracking
    email_message_id = db.Column(db.String(255), nullable=True)  # For email threading
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ticket = db.relationship('Ticket', back_populates='messages')
    user = db.relationship('User', back_populates='messages')
    admin = db.relationship('AdminUser', backref='messages')
    
    def __repr__(self):
        return f'<TicketMessage {self.id} for Ticket {self.ticket_id}>'
    
    @property
    def author_name(self):
        """Get author name"""
        if self.user:
            return self.user.name
        elif self.admin:
            return f"{self.admin.username} (Support)"
        return "System"
    
    @property
    def author_email(self):
        """Get author email"""
        if self.user:
            return self.user.email
        elif self.admin:
            return self.admin.email
        return None
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'author': self.author_name,
            'author_email': self.author_email,
            'message': self.message,
            'is_internal': self.is_internal,
            'created_at': self.created_at.isoformat()
        }