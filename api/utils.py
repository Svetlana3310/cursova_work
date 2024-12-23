from flask import jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt


def role_required(required_role):
    def wrapper(fn):
        @jwt_required()
        def decorated_function(*args, **kwargs):
            claims = get_jwt()  # Get all claims from the JWT
            identity = claims.get('sub')  # 'sub' contains the identity field
            if not identity or not isinstance(identity, dict):
                return jsonify({"message": "Invalid token structure"}), 403

            role = identity.get('role')  # Extract 'role' from the identity
            current_app.logger.info(f"User role: {role}")  # Log the role
            if role != required_role:
                return jsonify({"message": "Access forbidden: insufficient permissions"}), 403
            return fn(*args, **kwargs)
        return decorated_function
    return wrapper
