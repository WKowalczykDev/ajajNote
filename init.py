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

    # Create upload directory if it doesn't exist
    Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()

