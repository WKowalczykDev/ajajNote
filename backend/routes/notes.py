import os
import uuid
from datetime import datetime
from pathlib import Path

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from init import db          # Dwie kropki = katalog wyżej
from models import Note, User
from routes.user import admin_required # Jedna kropka = ten sam katalog
from textTransform.transform import transform

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')
ALLOWED_EXTENSIONS = {'mp3', 'wav'}


def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@notes_bp.route('/send', methods=['POST'])
@jwt_required()
def send_audio():
    """Endpoint to receive audio files"""
    identity = get_jwt_identity()
    user = User.query.filter_by(email=identity).first()
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        print(audio_file.filename)
        if not is_allowed_file(audio_file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: mp3, wav, ogg, m4a, flac'}), 400

        # Generate unique filename
        file_extension = audio_file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Save file
        file_path = user.private_directory / Path("uploads") /  unique_filename
        audio_file.save(str(file_path))

        # Get title from form data or use default
        title = request.form.get('title', f'Recording {datetime.now().strftime("%Y-%m-%d %H:%M")}')

        # Create database entry
        note = Note(
            title=title,
            user_id=user.id,
            filename=unique_filename,
            status='pending'
        )
        try:
            db.session.add(note)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        return jsonify({
            'message': 'Audio file uploaded successfully',
            'note_id': note.id,
            'filename': unique_filename
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notes_bp.route('/process/<int:note_id>', methods=['POST'])
@jwt_required()
def process_audio(note_id):
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    note = Note.query.filter_by(id=note_id).first()

    if not user:
        return jsonify({'error': 'No user found'}), 404

    if not note:
        return jsonify({'error': 'No note found'}), 404

    if not user.is_admin and note.user_id != user.id:
        return jsonify({'error': 'You are not authorized to process this note'}), 403

    if note.status == 'processed':
        return jsonify({'error': 'Note already processed'}), 400

    directories = get_user_directories(user)
    msg, status = transform(input = directories['uploads'],
              transcript_dir=directories['transcripts'],
              note=directories['md'],
              filename = note.filename)

    if status == 200:
        note.status = 'processed'
        transcript, note_content = read_note_files(note)

        try:
            note.transcription = transcript
            note.note_content = note_content
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()

    return jsonify({'message': msg}), status


def get_user_directories(user):
    """Get or create user's subdirectories"""
    base_dir = user.private_directory

    transcripts_dir = os.path.join(base_dir, 'transcripts')
    md_dir = os.path.join(base_dir, 'notes')
    uploads_dir = os.path.join(base_dir, 'uploads')

    for directory in [transcripts_dir, md_dir, uploads_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    return {
        'transcripts': transcripts_dir,
        'md': md_dir,
        'uploads': uploads_dir
    }

def read_note_files(note, user_dirs=None):
    """Read transcription and note content from files"""
    if user_dirs is None:
        user = User.query.get(note.user_id)
        user_dirs = get_user_directories(user)

    transcription = None
    note_content = None

    # Read transcription
    file = note.filename.split('.')[0]
    transcript_filename = f"{file}.txt"
    transcript_path = os.path.join(user_dirs['transcripts'], transcript_filename)
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcription = f.read()

    # Read note content
    md_filename = f"{file}.md"
    md_path = os.path.join(user_dirs['md'], md_filename)
    if os.path.exists(md_path):
        with open(md_path, 'r', encoding='utf-8') as f:
            note_content = f.read()

    return transcription, note_content

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id).first()
    identity = get_jwt_identity()
    user = User.query.filter_by(email=identity).first()
    note_owner = User.query.get(note.user_id)
    user_dirs = get_user_directories(user)

    if user.id != note_owner.id and  not user.is_admin:
        return jsonify({'error': 'You are not authorized to delete this note'}), 401

    # Delete transcription file
    file = note.filename.rstrip('.mp3')
    transcript_path = Path(user_dirs['transcripts'], f"{file}.txt")
    if os.path.exists(transcript_path):
        os.remove(transcript_path)

    audio_path = Path(user_dirs['uploads'], f"{file}.mp3")
    if os.path.exists(audio_path):
        os.remove(audio_path)

    # Delete note content file
    md_path = Path(user_dirs['md'], f"{file}.md")
    if os.path.exists(md_path):
        os.remove(md_path)
    try:
        db.session.delete(note)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()

    return jsonify({'status': 'success'}), 200

@notes_bp.route('', methods=['GET'])
@jwt_required()
def get_notes():
    """Get all notes for the current user"""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get query parameters for filtering
    status = request.args.get('status')

    # Build query
    query = Note.query.filter_by(user_id=user.id)

    if status:
        query = query.filter_by(status=status)

    notes = query.order_by(Note.created_at.desc()).all()

    return jsonify({
        'notes': [note.to_dict() for note in notes],
        'count': len(notes)
    }), 200

@notes_bp.route('get/<int:note_id>', methods=['POST'])
@jwt_required()
def get_note(note_id):
    """Get a specific note with full content from files"""
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # Check if user owns the note or is admin
    if note.user_id != user.id and not user.is_admin:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({'note': note.to_dict()}), 200


# # UPDATE - Update a note
# @notes_bp.route('/<int:note_id>', methods=['PUT', 'PATCH'])
# @jwt_required()
# def update_note(note_id):
#     """Update a note"""
#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)
#
#     if not user:
#         return jsonify({'error': 'User not found'}), 404
#
#     note = Note.query.get(note_id)
#
#     if not note:
#         return jsonify({'error': 'Note not found'}), 404
#
#     # Check if user owns the note
#     if note.user_id != current_user_id:
#         return jsonify({'error': 'Access denied'}), 403
#
#     data = request.get_json()
#
#     try:
#         # Update database fields
#         if 'title' in data:
#             note.title = data['title']
#
#         if 'meeting_time' in data:
#             note.meeting_time = datetime.fromisoformat(data['meeting_time']) if data['meeting_time'] else None
#
#         if 'status' in data:
#             note.status = data['status']
#
#         # Get user directories
#         user_dirs = get_user_directories(user)
#
#         # Update files if content is provided
#         if 'transcription' in data:
#             save_note_files(note, transcription=data['transcription'], user_dirs=user_dirs)
#             note.transcription = data['transcription']
#
#         if 'note_content' in data:
#             save_note_files(note, note_content=data['note_content'], user_dirs=user_dirs)
#             note.note_content = data['note_content']
#
#         note.updated_at = datetime.now()
#         db.session.commit()
#
#         return jsonify({
#             'message': 'Note updated successfully',
#             'note': note.to_dict()
#         }), 200
#
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': f'Failed to update note: {str(e)}'}), 500


# ADMIN - Get all notes (all users)
@notes_bp.route('/all', methods=['GET'])
@admin_required()
def admin_get_all_notes():
    """Admin endpoint to get all notes from all users"""
    status = request.args.get('status')
    user_id = request.args.get('user_id')

    query = Note.query

    if status:
        query = query.filter_by(status=status)

    if user_id:
        query = query.filter_by(user_id=user_id)

    notes = query.order_by(Note.created_at.desc()).all()

    # Include user information in response
    notes_with_users = []
    for note in notes:
        note_dict = note.to_dict()
        note_dict['user'] = {
            'id': note.user.id,
            'name': note.user.name,
            'email': note.user.email
        }
        notes_with_users.append(note_dict)

    return jsonify({
        'notes': notes_with_users,
        'count': len(notes_with_users)
    }), 200
