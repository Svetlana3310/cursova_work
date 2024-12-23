from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from api.models import db, User

auth = Blueprint('auth', __name__)

# Register a new user
# Endpoint: POST /auth/register
# Request JSON:
# {
#     "name": "John Doe",
#     "email": "john.doe@example.com",
#     "phone": "1234567890",
#     "password": "password123",
#     "role": "student"  # or "instructor"
# }
# Response: 
# { "message": "Student registered successfully!" }
@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    if 'role' not in data or data['role'] not in ['student', 'instructor']:
        return jsonify({"error": "Invalid role. Must be 'student' or 'instructor'"}), 400

    user = User(name=data['name'], email=data['email'], phone=data['phone'], role=data['role'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": f"{data['role'].capitalize()} registered successfully!"}), 201


# Login an existing user
# Endpoint: POST /auth/login
# Request JSON:
# {
#     "email": "john.doe@example.com",
#     "password": "password123"
# }
# Response:
# {
#     "token": "eyJhbGciOiJIUzI1NiIsInR..."
# }
@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        # Use user ID as the subject
        token = create_access_token(
            identity=str(user.id),  # Convert user ID to a string
            additional_claims={"role": user.role}  # Add role as a custom claim
        )
        return jsonify({"token": token}), 200
    return jsonify({"message": "Invalid credentials"}), 401