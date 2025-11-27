from datetime import datetime
from init import db


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    meeting_time = db.Column(db.DateTime, nullable=True)
    transcription = db.Column(db.Text, nullable=True)
    note_content = db.Column(db.Text, nullable=True)
    audio_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed

    def __repr__(self):
        return f'<Note {self.id}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'transcription': self.transcription,
            'meeting_time': self.meeting_time,
            'note_content': self.note_content,
            'audio_filename': self.audio_filename,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status
        }