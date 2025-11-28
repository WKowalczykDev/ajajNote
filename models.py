import os
import secrets
from datetime import datetime
from init import db


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    meeting_time = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transcription = db.Column(db.Text, nullable=True)
    note_content = db.Column(db.Text, nullable=True)
    audio_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed

    def __repr__(self):
        return f'<Note {self.id}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'transcription': self.transcription,
            'user_id': self.user_id,
            'meeting_time': self.meeting_time,
            'note_content': self.note_content,
            'audio_filename': self.audio_filename,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status
        }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    private_directory = db.Column(db.String(255), unique=True, nullable=False)
    notes = db.relationship('Note', backref='user', lazy='dynamic')
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        if include_sensitive:
            data['private_directory'] = self.private_directory
        return data

def create_user_directory(directory_name):
    """Create user's private directory"""
    base_path = 'user_files'
    full_path = os.path.join(base_path, directory_name)

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    return full_path

def generate_unique_directory_name(email):
    """Generate unique directory name for user"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_string = secrets.token_hex(4)
    safe_email = email.split('@')[0].replace('.', '_')
    return f"{safe_email}_{timestamp}_{random_string}"