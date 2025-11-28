import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models import Note, User
from routes.user import admin_required

notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')

def get_user_directories(user):
    """Get or create user's subdirectories"""
    base_dir = user.private_directory

    transcripts_dir = os.path.join(base_dir, 'transcripts')
    md_dir = os.path.join(base_dir, 'md')
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
    transcript_filename = f"note_{note.id}_transcript.txt"
    transcript_path = os.path.join(user_dirs['transcripts'], transcript_filename)
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcription = f.read()

    # Read note content
    md_filename = f"note_{note.id}_content.md"
    md_path = os.path.join(user_dirs['md'], md_filename)
    if os.path.exists(md_path):
        with open(md_path, 'r', encoding='utf-8') as f:
            note_content = f.read()

    return transcription, note_content


def delete_note_files(note):
    """Delete note files from disk"""
    user = User.query.get(note.user_id)
    user_dirs = get_user_directories(user)

    # Delete transcription file
    transcript_filename = f"note_{note.id}_transcript.txt"
    transcript_path = os.path.join(user_dirs['transcripts'], transcript_filename)
    if os.path.exists(transcript_path):
        os.remove(transcript_path)

    # Delete note content file
    md_filename = f"note_{note.id}_content.md"
    md_path = os.path.join(user_dirs['md'], md_filename)
    if os.path.exists(md_path):
        os.remove(md_path)

    # Note: We do NOT delete the audio file (mp3) from uploads directory

# READ - Get all notes for current user
@notes_bp.route('', methods=['GET'])
@jwt_required()
def get_notes():
    """Get all notes for the current user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get query parameters for filtering
    status = request.args.get('status')

    # Build query
    query = Note.query.filter_by(user_id=current_user_id)

    if status:
        query = query.filter_by(status=status)

    notes = query.order_by(Note.created_at.desc()).all()

    return jsonify({
        'notes': [note.to_dict() for note in notes],
        'count': len(notes)
    }), 200


# READ - Get a specific note by ID
@notes_bp.route('/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    """Get a specific note with full content from files"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # Check if user owns the note or is admin
    if note.user_id != current_user_id and not user.is_admin:
        return jsonify({'error': 'Access denied'}), 403

    # Read content from files
    user_dirs = get_user_directories(User.query.get(note.user_id))
    transcription, note_content = read_note_files(note, user_dirs)

    # Build response
    note_dict = note.to_dict()
    note_dict['transcription'] = transcription
    note_dict['note_content'] = note_content

    return jsonify({'note': note_dict}), 200


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


# DELETE - Delete own note (user)
@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """Delete a note (user can only delete their own)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # Check if user owns the note
    if note.user_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403

    try:
        # Delete files from disk
        delete_note_files(note)

        # Delete from database
        db.session.delete(note)
        db.session.commit()

        return jsonify({'message': 'Note deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete note: {str(e)}'}), 500


# ADMIN - Delete any note
@notes_bp.route('/admin/<int:note_id>', methods=['DELETE'])
@admin_required()
def admin_delete_note(note_id):
    """Admin endpoint to delete any note"""
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    try:
        # Delete files from disk
        delete_note_files(note)

        # Delete from database
        db.session.delete(note)
        db.session.commit()

        return jsonify({'message': 'Note deleted successfully by admin'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete note: {str(e)}'}), 500


# ADMIN - Get all notes (all users)
@notes_bp.route('/admin/all', methods=['GET'])
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
