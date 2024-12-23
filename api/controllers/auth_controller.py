from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from api.models import db, User

auth_bp = Blueprint('auth', __name__)

# Register a new user
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    Endpoint: POST /auth/register
    Request JSON:
    {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "password": "password123",
        "role": "student"  # or "instructor"
    }
    Response:
    {
        "message": "Student registered successfully!"
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input data"}), 400

    if 'role' not in data or data['role'] not in ['student', 'instructor']:
        return jsonify({"error": "Invalid role. Must be 'student' or 'instructor'"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        role=data['role']
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": f"{data['role'].capitalize()} registered successfully!"}), 201


# Login an existing user
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login an existing user.
    Endpoint: POST /auth/login
    Request JSON:
    {
        "email": "john.doe@example.com",
        "password": "password123"
    }
    Response:
    {
        "token": "eyJhbGciOiJIUzI1NiIsInR..."
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input data"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        token = create_access_token(
            identity={"id": user.id, "role": user.role},  # Use dictionary for identity
        )
        return jsonify({"token": token}), 200

    return jsonify({"error": "Invalid credentials"}), 401


# Logout user (if implemented with token revocation)
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout the user (requires valid JWT token).
    Endpoint: POST /auth/logout
    Response:
    {
        "message": "Successfully logged out"
    }
    """
    user_id = get_jwt_identity().get("id")
    return jsonify({"message": f"User {user_id} logged out successfully!"}), 200