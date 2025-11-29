from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt, set_access_cookies, unset_jwt_cookies, get_csrf_token
)
from functools import wraps
import datetime
import os
from models import User
from init import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Decorators
def admin_required():
    """Decorator to require admin privileges"""

    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            email = get_jwt_identity()
            is_admin = User.query.filter_by(email=email).first().is_admin
            if not is_admin:
                return jsonify({'error': 'Admin privileges required'}), 403
            return fn(*args, **kwargs)

        return decorator

    return wrapper


# Authentication Routes

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    data = request.get_json()

    # Validate input
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Name, email and password are required'}), 400

    email = data['email'].lower().strip()
    name = data['name'].strip()
    password = data['password']

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Create new user
    password_hash = generate_password_hash(password)

    new_user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        is_admin=False
    )


    try:
        db.session.add(new_user)
        db.session.flush()
        new_user.create_user_directory()
        db.session.commit()

        # Create user director

        # Generate tokens
        access_token = create_access_token(identity=new_user.email)
        refresh_token = create_refresh_token(identity=new_user.email)

        resp = jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': new_user.to_dict()
        })
        set_access_cookies(resp, access_token)

        return resp, 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def signin():
    """Sign in existing user"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email'].lower().strip()
    password = data['password']

    # Find user
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Update last login
    user.last_login = datetime.datetime.now()
    db.session.commit()

    # Generate tokens
    access_token = create_access_token(identity=user.email)
    refresh_token = create_refresh_token(identity=user.email)

    resp = jsonify({
        'message': 'Sign in successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(include_sensitive=True)
    })
    set_access_cookies(resp, access_token)

    return resp , 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    resp = jsonify({'message': 'Signed out successfully'})
    unset_jwt_cookies(resp)
    return resp, 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(email=current_user_id).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user.to_dict(include_sensitive=True)}), 200


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user information"""
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(email=current_user_id).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update allowed fields
    if 'name' in data:
        user.name = data['name'].strip()

    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])

    try:
        db.session.commit()
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update user: {str(e)}'}), 500


@auth_bp.route('/users', methods=['GET'])
@admin_required()
def get_all_users():
    """Get all users (Admin only)"""
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users],
        'total': len(users)
    }), 200


@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required()
def get_user(user_id):
    """Get specific user by ID (Admin only)"""
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user.to_dict(include_sensitive=True)}), 200


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required()
def update_user(user_id):
    """Update user by ID (Admin only)"""
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update fields
    if 'name' in data:
        user.name = data['name'].strip()

    if 'email' in data:
        new_email = data['email'].lower().strip()
        # Check if email is already taken by another user
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email already in use'}), 409
        user.email = new_email

    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])

    if 'is_admin' in data:
        user.is_admin = bool(data['is_admin'])

    try:
        db.session.commit()
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update user: {str(e)}'}), 500


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    """Delete user by ID (Admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Prevent admin from deleting themselves
    if user.id == current_user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400

    try:
        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'User deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500
