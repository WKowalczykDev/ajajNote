import requests
import os
import uuid
from datetime import datetime
from pathlib import Path

from flask import send_file
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from init import db
from models import Note, User
from routes.user import admin_required

# Adres mikroserwisu zdefiniowany w docker-compose
TEXT_TRANSFORM_URL = os.getenv('TEXT_TRANSFORM_URL', 'http://text-transform:5001')

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
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not is_allowed_file(audio_file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: mp3, wav, ogg, m4a, flac'}), 400

        # Generate unique filename
        file_extension = audio_file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Save file to shared volume
        file_path = user.private_directory / Path("uploads") / unique_filename
        audio_file.save(str(file_path))

        # Get title
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
    """
    Wysyła żądanie przetworzenia notatki do mikroserwisu textTransform.
    """
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    note = Note.query.filter_by(id=note_id).first()

    # Walidacja uprawnień i istnienia zasobów
    if not user:
        return jsonify({'error': 'No user found'}), 404

    if not note:
        return jsonify({'error': 'No note found'}), 404

    if not user.is_admin and note.user_id != user.id:
        return jsonify({'error': 'You are not authorized to process this note'}), 403

    if note.status == 'processed':
        return jsonify({'error': 'Note already processed'}), 400

    # Komunikacja z mikroserwisem textTransform
    try:
        # Wysyłamy filename i user_id, mikroserwis sam ogarnie ścieżki na współdzielonym wolumenie
        response = requests.post(f"{TEXT_TRANSFORM_URL}/process", json={
            "filename": note.filename,
            "user_id": user.id
        })

        # Sprawdzamy czy mikroserwis nie zwrócił błędu
        if response.status_code != 200:
            try:
                error_msg = response.json().get('message', 'Unknown error')
            except:
                error_msg = response.text
            return jsonify({'error': f'Processing service error: {error_msg}'}), response.status_code

        response_data = response.json()
        msg = response_data.get('message', 'Success')

        # Sukces - aktualizacja bazy danych
        note.status = 'processed'

        # Odczytujemy wyniki, które mikroserwis zapisał na dysku
        transcript, note_content = read_note_files(note)

        try:
            note.transcription = transcript
            note.note_content = note_content
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Database error during update'}), 500

        return jsonify({'message': msg}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Communication with processing service failed: {str(e)}'}), 503


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

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    note_owner = User.query.get(note.user_id)
    user_dirs = get_user_directories(user if user.is_admin else note_owner)

    if user.id != note_owner.id and not user.is_admin:
        return jsonify({'error': 'You are not authorized to delete this note'}), 401

    # Delete transcription file
    file = note.filename.rsplit('.', 1)[0]
    transcript_path = Path(user_dirs['transcripts'], f"{file}.txt")
    if os.path.exists(transcript_path):
        os.remove(transcript_path)

    audio_path = Path(user_dirs['uploads'], note.filename)
    if os.path.exists(audio_path):
        os.remove(audio_path)

    # Delete note content file
    md_path = Path(user_dirs['md'], f"{file}.md")
    if os.path.exists(md_path):
        os.remove(md_path)
    try:
        db.session.delete(note)
        db.session.commit()
    except IntegrityError:
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
        if note.user:
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


@notes_bp.route('/<int:note_id>/export/pdf', methods=['GET'])
@jwt_required()
def export_note_pdf(note_id):
    """Export note to PDF"""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # Sprawdzenie uprawnień
    if note.user_id != user.id and not user.is_admin:
        return jsonify({'error': 'Access denied'}), 403

    # Pobranie treści
    transcript, note_content = read_note_files(note)

    # Tworzenie PDF w pamięci
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    # Prosta konfiguracja czcionki (uwaga: domyślna czcionka może nie obsługiwać polskich znaków)
    # Aby w pełni obsługiwać PL znaki, należałoby załadować czcionkę .ttf (np. Arial)
    # Tutaj używamy standardowej Helveticy, która może nie wyświetlać "ąę" poprawnie bez dodatkowej konfiguracji
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, f"Notatka: {note.title}")
    y -= 30

    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Data: {note.created_at}")
    y -= 50

    # Funkcja pomocnicza do pisania tekstu wielowierszowego
    def draw_text_block(text, y_pos):
        if not text:
            return y_pos
        text_lines = text.split('\n')
        for line in text_lines:
            if y_pos < 50:
                p.showPage()
                p.setFont("Helvetica", 12)
                y_pos = height - 50

            # Proste zawijanie tekstu (dla pełnej obsługi warto użyć Paragraph z reportlab.platypus)
            # Tutaj wersja uproszczona ucinająca zbyt długie linie
            p.drawString(50, y_pos, line[:80])
            y_pos -= 15
        return y_pos

    if note_content:
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Podsumowanie:")
        y -= 25
        p.setFont("Helvetica", 12)
        y = draw_text_block(note_content, y)
        y -= 30

    if transcript:
        if y < 100:
            p.showPage()
            y = height - 50
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Transkrypcja:")
        y -= 25
        p.setFont("Helvetica", 12)
        draw_text_block(transcript, y)

    p.save()
    buffer.seek(0)

    filename = f"{note.filename.rsplit('.', 1)[0]}.pdf"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )