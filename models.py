import os
import secrets
import shutil
from datetime import datetime

from flask import current_app

from init import db


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    meeting_time = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transcription = db.Column(db.Text, nullable=True)
    note_content = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
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
            'filename': self.filename,
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
    private_directory = db.Column(db.String(255), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    notes = db.relationship('Note', backref='user', lazy='dynamic')

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
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'private_directory': self.private_directory
        }
        if include_sensitive:
            data['private_directory'] = self.private_directory
        return data

    def create_user_directory(self):
        """Create user's private directory"""
        base_path = current_app.config['UPLOAD_FOLDER']
        full_path = os.path.join(base_path, str(self.id))

        if not os.path.exists(base_path):
            os.makedirs(base_path)

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        upload_path =  os.path.join(full_path, "uploads")
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        transcription_path = os.path.join(full_path, "transcripts")
        if not os.path.exists(transcription_path):
            os.makedirs(transcription_path)

        md_path = os.path.join(full_path, "notes")
        if not os.path.exists(md_path):
            os.makedirs(md_path)


        self.private_directory = full_path

    def delete_user_directory(self):
        """Delete user's private directory"""
        try:
            os.rmdir(self.private_directory)
        except OSError:
            print("Directory not empty! Using force delete instead...")
            shutil.rmtree(self.private_directory)  # removes directory and all contents


