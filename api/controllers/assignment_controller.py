from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.models import db, Assignment
from api.utils import role_required

assignment_bp = Blueprint('assignment', __name__)

# Create a new assignment
@assignment_bp.route('/create', methods=['POST'], endpoint='create_assignment')
@role_required('instructor')
def create_assignment():
    """
    Create a new assignment. Endpoint: POST /assignments/create (Instructor only)
    Expects JSON:
    {
        "title": "Assignment Title",
        "description": "Assignment Description",
        "due_date": "YYYY-MM-DD",
        "course_id": int
    }
    Response:
    {
        "message": "Assignment created successfully!"
    }
    """
    data = request.json
    if not data or 'title' not in data or 'description' not in data or 'due_date' not in data or 'course_id' not in data:
        return jsonify({"message": "Invalid data provided"}), 400

    assignment = Assignment(
        title=data['title'],
        description=data['description'],
        due_date=data['due_date'],
        course_id=data['course_id']
    )
    db.session.add(assignment)
    db.session.commit()
    return jsonify({"message": "Assignment created successfully!"}), 201

# Get assignments for a course
@assignment_bp.route('/course/<int:course_id>', methods=['GET'], endpoint='get_assignment')
@jwt_required()
def get_course_assignments(course_id):
    """
    Get assignments for a course. Endpoint: GET /assignments/course/<course_id>
    Response:
    [
        {
            "id": int,
            "title": "Assignment Title",
            "description": "Assignment Description",
            "due_date": "YYYY-MM-DD"
        },
        ...
    ]
    """
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    return jsonify([{
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "due_date": assignment.due_date.isoformat() if assignment.due_date else None
    } for assignment in assignments]), 200