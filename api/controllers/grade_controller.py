from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.models import db, Grade
from api.utils import role_required

grade_bp = Blueprint('grade', __name__)

# Assign a grade to a student
@grade_bp.route('/assign', methods=['POST'], endpoint='create_assign')
@role_required('instructor')
def assign_grade():
    """
    Assign a grade to a student. Endpoint: POST /grades/assign (Instructor only)
    Expects JSON:
    {
        "assignment_id": int,
        "student_id": int,
        "grade": float
    }
    Response:
    {
        "message": "Grade assigned successfully!"
    }
    """
    data = request.json
    if not data or 'assignment_id' not in data or 'student_id' not in data or 'grade' not in data:
        return jsonify({"message": "Invalid data provided"}), 400

    grade = Grade(
        assignment_id=data['assignment_id'],
        student_id=data['student_id'],
        grade=data['grade']
    )
    db.session.add(grade)
    db.session.commit()
    return jsonify({"message": "Grade assigned successfully!"}), 201