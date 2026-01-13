import os
from flask import Flask
from pathlib import Path
from werkzeug.security import generate_password_hash
from flask_cors import CORS

from extensions import jwt, db
from models import User


def create_app():
    app = Flask(__name__)

    # =========================================================================
    # KONFIGURACJA CORS
    # =========================================================================
    # Używamy resources, co jest najbardziej stabilnym sposobem dla Flask-CORS
    CORS(app,
         resources={r"/*": {
             "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
         }},
         supports_credentials=True)

    # =========================================================================
    # KONFIGURACJA APLIKACJI
    # =========================================================================

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///transcriptions.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    upload_folder_path = os.getenv('UPLOAD_FOLDER', '../database/Users')
    app.config['UPLOAD_FOLDER'] = Path(upload_folder_path)
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

    # Konfiguracja JWT
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    # WAŻNE: W dev (localhost) SECURE musi być False, bo nie masz HTTPS
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_HTTPONLY"] = True
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    # SameSite='Lax' jest wymagane, aby cookies działały między portami na localhost
    app.config["JWT_COOKIE_SAMESITE"] = "Lax"

    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)

    from routes.user import auth_bp
    app.register_blueprint(auth_bp)

    from routes.notes import notes_bp
    app.register_blueprint(notes_bp)

    with app.app_context():
        db.create_all()

    init_admin_user(app)

    return app


def init_admin_user(app):
    with app.app_context():
        try:
            admin = User.query.filter_by(is_admin=True).first()
            if not admin:
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
                if hasattr(admin, 'create_user_directory'):
                     admin.create_user_directory()
                print(f"Admin user created - Email: admin@system.com")
        except Exception as e:
            print(f"Admin initialization skipped or failed: {e}")


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)