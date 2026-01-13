import os
from flask import Flask
from pathlib import Path
from werkzeug.security import generate_password_hash
from flask_cors import CORS  # <--- WAŻNE: Import CORS

from extensions import jwt, db
from models import User


def create_app():
    app = Flask(__name__)

    # =========================================================================
    # KONFIGURACJA CORS
    # Zezwalamy na żądania z localhost:5173 (Frontend) i obsługę ciasteczek
    # =========================================================================
    CORS(app,
         resources={r"/*": {"origins": ["http://localhost:5173"]}},
         supports_credentials=True)

    # =========================================================================
    # KONFIGURACJA APLIKACJI (Pod Docker i Localhost)
    # =========================================================================

    # Klucz sekretny (pobierany z env lub domyślny dla dev)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    # Baza danych: W Dockerze używamy ścieżki z ENV, lokalnie fallback
    # W docker-compose ustawimy to na: sqlite:////app/data/transcriptions.db
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///transcriptions.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Folder uploadu: W Dockerze to /app/data, lokalnie ../database/Users
    upload_folder_path = os.getenv('UPLOAD_FOLDER', '../database/Users')
    app.config['UPLOAD_FOLDER'] = Path(upload_folder_path)

    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB limit

    # Konfiguracja JWT (Ciasteczka)
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"

    # WAŻNE: False dla localhost (http), True dla produkcji (https)
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_HTTPONLY"] = True
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # WAŻNE: Lax pozwala na przesyłanie ciasteczek między portami localhosta
    app.config["JWT_COOKIE_SAMESITE"] = "Lax"

    # Tworzenie folderu uploadu jeśli nie istnieje
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    # Inicjalizacja rozszerzeń
    db.init_app(app)
    jwt.init_app(app)

    # Rejestracja Blueprintów
    from routes.user import auth_bp
    app.register_blueprint(auth_bp)

    from routes.notes import notes_bp
    app.register_blueprint(notes_bp)

    # Tworzenie tabel bazy danych
    with app.app_context():
        db.create_all()

    # Inicjalizacja admina
    init_admin_user(app)

    return app


def init_admin_user(app):
    """Tworzy użytkownika admina przy starcie, jeśli nie istnieje"""
    with app.app_context():
        try:
            # Sprawdzamy czy tabela users w ogóle istnieje (unikamy błędu przy pierwszym uruchomieniu)
            admin = User.query.filter_by(is_admin=True).first()

            if not admin:
                # Pobieramy hasło z ENV (zdefiniowane w docker-compose)
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
                password_hash = generate_password_hash(admin_password)

                admin = User(
                    name='Administrator',
                    email='admin@system.com',
                    password_hash=password_hash,
                    is_admin=True
                )

                db.session.add(admin)
                db.session.commit()

                # Tworzymy katalogi dla admina
                admin.create_user_directory()

                print(f"Admin user created - Email: admin@system.com, Password: {admin_password}")
        except Exception as e:
            print(f"Admin initialization skipped or failed: {e}")


if __name__ == '__main__':
    app = create_app()