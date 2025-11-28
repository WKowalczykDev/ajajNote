from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcriptions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = Path('uploads')
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 50MB max file size
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_COOKIE_SECURE"] = True  # only HTTPS
    app.config["JWT_COOKIE_HTTPONLY"] = True  # JS cannot read cookie
    app.config["JWT_COOKIE_SAMESITE"] = "Strict"

    # Create upload directory if it doesn't exist
    Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes.main import main_bp
    app.register_blueprint(main_bp)

    from routes.user import auth_bp
    app.register_blueprint(auth_bp)

    from routes.notes import  notes_bp
    app.register_blueprint(notes_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()

