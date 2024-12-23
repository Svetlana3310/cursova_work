from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from api.models import db, User, Course, Assignment, Enrollment, Grade

analytics_bp = Blueprint('analytics', __name__)

# Get course with assignments and students


@analytics_bp.route('/course-details/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_details(course_id):
    """
    Get course details with assignments and enrolled students.
    Endpoint: GET /analytics/course-details/<course_id>
    """
    results = db.session.query(
        Course.id.label('course_id'),
        Course.name.label('course_name'),
        Assignment.id.label('assignment_id'),
        Assignment.title.label('assignment_title'),
        User.id.label('student_id'),
        User.name.label('student_name')
    ).join(
        Assignment, Assignment.course_id == Course.id, isouter=True
    ).join(
        Enrollment, Enrollment.course_id == Course.id, isouter=True
    ).join(
        User, User.id == Enrollment.student_id, isouter=True
    ).filter(Course.id == course_id).all()

    return jsonify([{
        "course_id": r.course_id,
        "course_name": r.course_name,
        "assignment_id": r.assignment_id,
        "assignment_title": r.assignment_title,
        "student_id": r.student_id,
        "student_name": r.student_name
    } for r in results]), 200

# Get average grades per student for a course


@analytics_bp.route('/average-grades/<int:course_id>', methods=['GET'])
@jwt_required()
def get_average_grades(course_id):
    """
    Get average grades per student for a specific course.
    Endpoint: GET /analytics/average-grades/<course_id>
    """
    results = db.session.query(
        User.id.label('student_id'),
        User.name.label('student_name'),
        db.func.avg(Grade.grade).label('average_grade')
    ).join(
        Grade, Grade.student_id == User.id
    ).join(
        Assignment, Assignment.id == Grade.assignment_id
    ).join(
        Course, Course.id == Assignment.course_id
    ).filter(Course.id == course_id).group_by(User.id, User.name).all()

    return jsonify([{
        "student_id": r.student_id,
        "student_name": r.student_name,
        "average_grade": r.average_grade
    } for r in results]), 200

# Get courses with student count


@analytics_bp.route('/courses-student-count', methods=['GET'])
@jwt_required()
def get_courses_with_student_count():
    """
    Get courses with the number of enrolled students.
    Endpoint: GET /analytics/courses-student-count
    """
    results = db.session.query(
        Course.id.label('course_id'),
        Course.name.label('course_name'),
        db.func.count(Enrollment.student_id).label('student_count')
    ).join(
        Enrollment, Enrollment.course_id == Course.id, isouter=True
    ).group_by(Course.id, Course.name).all()

    return jsonify([{
        "course_id": r.course_id,
        "course_name": r.course_name,
        "student_count": r.student_count
    } for r in results]), 200

# Get students without grades for a course


@analytics_bp.route('/students-no-grades/<int:course_id>', methods=['GET'])
@jwt_required()
def get_students_without_grades(course_id):
    """
    Get students without grades for a specific course.
    Endpoint: GET /analytics/students-no-grades/<course_id>
    """
    subquery = db.session.query(Grade.student_id).join(
        Assignment).filter(Assignment.course_id == course_id).subquery()
    results = db.session.query(
        User.id.label('student_id'),
        User.name.label('student_name')
    ).join(
        Enrollment, Enrollment.student_id == User.id
    ).filter(
        Enrollment.course_id == course_id,
        ~User.id.in_(subquery)
    ).all()

    return jsonify([{
        "student_id": r.student_id,
        "student_name": r.student_name
    } for r in results]), 200

# Get courses with the highest number of assignments


@analytics_bp.route('/courses-highest-assignments', methods=['GET'])
@jwt_required()
def get_courses_with_highest_assignments():
    """
    Get courses with the highest number of assignments.
    Endpoint: GET /analytics/courses-highest-assignments
    """
    results = db.session.query(
        Course.id.label('course_id'),
        Course.name.label('course_name'),
        db.func.count(Assignment.id).label('assignment_count')
    ).join(
        Assignment, Assignment.course_id == Course.id, isouter=True
    ).group_by(Course.id, Course.name).order_by(db.func.count(Assignment.id).desc()).all()

    return jsonify([{
        "course_id": r.course_id,
        "course_name": r.course_name,
        "assignment_count": r.assignment_count
    } for r in results]), 200
