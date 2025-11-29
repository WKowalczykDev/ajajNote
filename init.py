import os

from flask import Flask
from pathlib import Path

from werkzeug.security import generate_password_hash

from extensions import jwt, db
from models import User


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcriptions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = Path('Users')
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 50MB max file size
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_COOKIE_SECURE"] = True  # only HTTPS
    app.config["JWT_COOKIE_HTTPONLY"] = True  # JS cannot read cookie
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # JS cannot read cookie #TODO
    app.config["JWT_COOKIE_SAMESITE"] = "Strict"
    app.config["ADMIN_LOGIN"] = "admin"
    app.config["ADMIN_PASSWORD"] = "admin123"

    # Create upload directory if it doesn't exist
    Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    from routes.user import auth_bp
    app.register_blueprint(auth_bp)

    from routes.notes import  notes_bp
    app.register_blueprint(notes_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    init_admin_user(app)


    return app

# Initialize function to create admin user
def init_admin_user(app):
    """Create initial admin user if none exists"""
    with app.app_context():
        admin = User.query.filter_by(is_admin=True).first()

        if not admin:
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')  # Change this!
            password_hash = generate_password_hash(admin_password)

            admin = User(
                name='Administrator',
                email='admin@system.com',
                password_hash=password_hash,
                is_admin=True
            )

            db.session.add(admin)
            db.session.commit()

            admin.create_user_directory()

            print(f"Admin user created - Email: admin@system.com, Password: {admin_password}")
            print("Please change the admin password immediately!")


if __name__ == '__main__':
    app = create_app()



