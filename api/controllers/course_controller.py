from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from api.models import db, Course
from api.utils import role_required

course_bp = Blueprint('course', __name__)

# Create a new course


@course_bp.route('/test-token', methods=['GET'])
@jwt_required()
def test_token():
    """
    Test token validation. Endpoint: GET /test-token
    Requires a valid JWT token.
    Response:
    {
        "identity": {"id": user_id, "role": "role"},
        "claims": { ... }  # Entire JWT claims
    }
    """
    try:
        claims = get_jwt()  # Get the entire JWT claims
        identity = claims.get('sub')  # Extract the 'identity' (sub field)

        if not identity:
            current_app.logger.error("Invalid token: 'sub' field is missing")
            return jsonify({"error": "Invalid token structure"}), 400

        current_app.logger.info(f"JWT Claims: {claims}")
        current_app.logger.info(f"Identity: {identity}")

        return jsonify({
            "identity": identity,
            "claims": claims
        }), 200
    except Exception as e:
        current_app.logger.error(f"Token validation failed: {e}")
        return jsonify({"error": "Token validation failed", "message": str(e)}), 401


@course_bp.route('/create', methods=['POST'], endpoint="create_course")
@role_required('instructor')
def create_course_instructor():
    """
    Create a new course. Endpoint: POST /create (Instructor only)
    Expects JSON:
    {
        "name": "Course Name",
        "description": "Course Description"
    }
    Response:
    {
        "message": "Course created successfully!"
    }
    """
    data = request.json

    # Validate incoming JSON format
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON format"}), 400

    # Define required fields and validate
    required_fields = ['name', 'description']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    # Validate each field is of the correct type
    for field in required_fields:
        if not isinstance(data[field], str):
            return jsonify({"message": f"{field.capitalize()} must be a string"}), 400

    # Check for unexpected fields in the payload
    extra_fields = [key for key in data if key not in required_fields]
    if extra_fields:
        return jsonify({"message": f"Unexpected fields: {', '.join(extra_fields)}"}), 400

    # Proceed to create the course
    instructor_id = get_jwt_identity()
    course = Course(
        name=data['name'],
        description=data['description'],
        instructor_id=int(instructor_id)
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({"message": "Course created successfully!"}), 201


# Get all courses
@course_bp.route('/list', methods=['GET'], endpoint='get_all_courses')
@jwt_required()
def get_courses():
    """
    Get all courses. Endpoint: GET /courses/list
    Response:
    [
        {
            "id": int,
            "name": "Course Name",
            "description": "Course Description"
        },
        ...
    ]
    """
    courses = Course.query.all()
    return jsonify([{
        "id": course.id,
        "name": course.name,
        "description": course.description
    } for course in courses]), 200

# Update a course


@course_bp.route('/update/<int:course_id>', methods=['PUT'], endpoint='update_course')
@role_required('instructor')
def update_course(course_id):
    """
    Update a course. Endpoint: PUT /courses/update/<course_id> (Instructor only)
    Expects JSON:
    {
        "name": "Updated Course Name",
        "description": "Updated Course Description"
    }
    Response:
    {
        "message": "Course updated successfully!"
    }
    """
    data = request.json
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404

    course.name = data.get('name', course.name)
    course.description = data.get('description', course.description)
    db.session.commit()
    return jsonify({"message": "Course updated successfully!"}), 200
