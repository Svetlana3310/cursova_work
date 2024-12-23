from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, Enrollment
from api.utils import role_required

enrollment_bp = Blueprint('enrollment', __name__)

# Enroll in a course
@enrollment_bp.route('/enroll', methods=['POST'], endpoint='create_enroll')
@role_required('student')
def enroll_in_course():
    """
    Enroll in a course. Endpoint: POST /enrollments/enroll (Student only)
    Expects JSON:
    {
        "course_id": int
    }
    Response:
    {
        "message": "Enrolled successfully!"
    }
    """
    data = request.json
    if not data or 'course_id' not in data:
        return jsonify({"message": "Invalid data provided"}), 400

    student_id = get_jwt_identity().get('id')
    enrollment = Enrollment(
        student_id=student_id,
        course_id=data['course_id']
    )
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({"message": "Enrolled successfully!"}), 201

# Get student enrollments
@enrollment_bp.route('/list', methods=['GET'], endpoint='get_student_enrollments')
@role_required('student')
def get_student_enrollments():
    """
    Get student enrollments. Endpoint: GET /enrollments/list (Student only)
    Response:
    [
        {
            "course_id": int,
            "enrolled_date": "YYYY-MM-DD"
        },
        ...
    ]
    """
    student_id = get_jwt_identity().get('id')
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    return jsonify([{
        "course_id": enrollment.course_id,
        "enrolled_date": enrollment.enrolled_date.isoformat() if enrollment.enrolled_date else None
    } for enrollment in enrollments]), 200