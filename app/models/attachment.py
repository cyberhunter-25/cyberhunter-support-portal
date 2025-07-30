"""
File attachment model
"""
import os
from datetime import datetime
from app.extensions import db


class Attachment(db.Model):
    """File attachment model"""
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False, index=True)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=True)
    
    # Security
    virus_scanned = db.Column(db.Boolean, default=False, nullable=False)
    scan_result = db.Column(db.String(255), nullable=True)
    
    # Upload information
    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    uploaded_by_admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ticket = db.relationship('Ticket', back_populates='attachments')
    uploaded_by_user = db.relationship('User', backref='uploaded_files')
    uploaded_by_admin = db.relationship('AdminUser', backref='uploaded_files')
    
    def __repr__(self):
        return f'<Attachment {self.filename} for Ticket {self.ticket_id}>'
    
    @property
    def uploader_name(self):
        """Get uploader name"""
        if self.uploaded_by_user:
            return self.uploaded_by_user.name
        elif self.uploaded_by_admin:
            return f"{self.uploaded_by_admin.username} (Support)"
        return "Unknown"
    
    @property
    def file_size_human(self):
        """Get human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @property
    def is_image(self):
        """Check if file is an image"""
        if not self.mime_type:
            return False
        return self.mime_type.startswith('image/')
    
    @property
    def is_safe(self):
        """Check if file passed virus scan"""
        return self.virus_scanned and self.scan_result == 'clean'
    
    def mark_as_scanned(self, result='clean'):
        """Mark file as scanned"""
        self.virus_scanned = True
        self.scan_result = result
        db.session.commit()
    
    def delete_file(self):
        """Delete physical file"""
        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
                return True
            except Exception:
                return False
        return True
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'filename': self.original_filename,
            'size': self.file_size_human,
            'mime_type': self.mime_type,
            'is_image': self.is_image,
            'is_safe': self.is_safe,
            'uploader': self.uploader_name,
            'created_at': self.created_at.isoformat()
        }