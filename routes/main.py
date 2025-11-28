from flask import Blueprint, render_template, request, jsonify, current_app
from pathlib import Path
import uuid
from datetime import datetime
from init import db
from models import Note
from textTransform.transform import transform

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'mp3', 'wav'}


def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route('/send', methods=['POST'])
def send_audio():
    """Endpoint to receive audio files"""
    print(request.files)
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
        upload_path = Path(current_app.config['UPLOAD_FOLDER'])
        file_path = upload_path / unique_filename
        audio_file.save(str(file_path))

        # Get title from form data or use default
        title = request.form.get('title', f'Recording {datetime.now().strftime("%Y-%m-%d %H:%M")}')

        # Create database entry
        note = Note(
            title=title,
            audio_filename=unique_filename,
            status='pending'
        )

        db.session.add(note)
        db.session.commit()

        transform(unique_filename.split('.')[0])

        return jsonify({
            'message': 'Audio file uploaded successfully',
            'note_id': note.id,
            'filename': unique_filename
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main_bp.route('/notes', methods=['GET'])
def get_notes():
    """Get all notes as JSON"""
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])


@main_bp.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note"""
    note = Note.query.get_or_404(note_id)
    return jsonify(note.to_dict())


@main_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a note's transcription or content"""
    note = Note.query.get_or_404(note_id)

    data = request.get_json()

    if 'transcription' in data:
        note.transcription = data['transcription']

    if 'note_content' in data:
        note.note_content = data['note_content']

    if 'status' in data:
        note.status = data['status']

    if 'title' in data:
        note.title = data['title']

    db.session.commit()

    return jsonify(note.to_dict())


@main_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note and its audio file"""
    note = Note.query.get_or_404(note_id)

    # Delete audio file
    file_path = Path(current_app.config['UPLOAD_FOLDER']) / note.audio_filename
    if file_path.exists():
        file_path.unlink()

    db.session.delete(note)
    db.session.commit()

    return jsonify({'message': 'Note deleted successfully'})


