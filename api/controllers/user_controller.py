from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, User
from api.utils import role_required

# Define the user blueprint
user_bp = Blueprint('user', __name__)

# Get all users (Instructor only)
@user_bp.route('/', methods=['GET'], endpoint='get_all_user')
@role_required('instructor')
def get_all_users():
    """
    Get all users. Endpoint: GET /users (Instructor only)
    Response:
    [
        {
            "id": int,
            "name": str,
            "email": str,
            "phone": str,
            "role": str
        },
        ...
    ]
    """
    users = User.query.all()
    return jsonify([{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role
    } for user in users]), 200

# Get a user by ID
@user_bp.route('/<int:user_id>', methods=['GET'], endpoint='get_user_by_id')
@jwt_required()
def get_user(user_id):
    """
    Get a user by ID. Endpoint: GET /users/<user_id>
    Response:
    {
        "id": int,
        "name": str,
        "email": str,
        "phone": str,
        "role": str
    }
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role
    }), 200

# Update a user by ID
@user_bp.route('/<int:user_id>', methods=['PUT'], endpoint='update_user')
@jwt_required()
def update_user(user_id):
    """
    Update a user by ID. Endpoint: PUT /users/<user_id>
    Expects JSON:
    {
        "name": str,
        "email": str,
        "phone": str,
        "role": str
    }
    Response:
    {
        "message": "User updated successfully!"
    }
    """
    data = request.json
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({"message": "User updated successfully!"}), 200

# Delete a user by ID (Instructor only)
@user_bp.route('/<int:user_id>', methods=['DELETE'], endpoint='delete_user')
@role_required('instructor')
def delete_user(user_id):
    """
    Delete a user by ID. Endpoint: DELETE /users/<user_id> (Instructor only)
    Response:
    {
        "message": "User deleted successfully!"
    }
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully!"}), 200