from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, Course, Enrollment, Assignment, Grade
from api.utils import role_required

routes = Blueprint('routes', __name__)

@routes.route('/test-token', methods=['GET'])
@jwt_required()
def test_token():
    """
    Test token validation. Endpoint: GET /test-token
    Requires a valid JWT token.
    Response: 
    {
        "identity": "user_id"
    }
    """
    try:
        identity = get_jwt_identity()
        current_app.logger.info(f"Identity: {identity}")
        return jsonify({"identity": identity}), 200
    except Exception as e:
        current_app.logger.error(f"Token validation failed: {e}")
        return jsonify({"error": "Token validation failed", "message": str(e)}), 401
    
@routes.route('/users', methods=['GET'])
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
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "phone": u.phone,
        "role": u.role
    } for u in users]), 200

@routes.route('/users/<int:user_id>', methods=['GET'])
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

@routes.route('/users/<int:user_id>', methods=['PUT'])
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

@routes.route('/users/<int:user_id>', methods=['DELETE'])
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


@routes.route('/courses', methods=['POST'], endpoint="create_course")
@role_required('instructor')
def create_course_instructor():
    """
    Create a new course. Endpoint: POST /courses (Instructor only)
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
    if not data or 'name' not in data or 'description' not in data:
        return jsonify({"message": "Invalid data provided"}), 400

    instructor_id = get_jwt_identity()
    course = Course(
        name=data['name'],
        description=data['description'],
        instructor_id=int(instructor_id)
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({"message": "Course created successfully!"}), 201

@routes.route('/courses', methods=['GET'], endpoint="get_course")
@jwt_required()
def get_courses_all():
    """
    Get all courses. Endpoint: GET /courses
    Response: 
    [
        {
            "id": int,
            "name": str,
            "description": str
        },
        ...
    ]
    """
    courses = Course.query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "description": c.description
    } for c in courses]), 200

@routes.route('/courses/<int:course_id>', methods=['PUT'])
@role_required('instructor')
def update_course(course_id):
    """
    Update a course. Endpoint: PUT /courses/<course_id> (Instructor only)
    Expects JSON:
    {
        "name": str,
        "description": str
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


@routes.route('/enrollments', methods=['POST'], endpoint="create_enrollments")
@role_required('student')
def enroll_in_course_student():
    """
    Enroll in a course. Endpoint: POST /enrollments (Student only)
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

    student_id = get_jwt_identity()
    enrollment = Enrollment(
        student_id=int(student_id),
        course_id=data['course_id']
    )
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({"message": "Enrolled successfully!"}), 201

@routes.route('/enrollments', methods=['GET'], endpoint="get_enrollments")
@role_required('student')
def get_student_enrollments():
    """
    Get student enrollments. Endpoint: GET /enrollments (Student only)
    Response:
    [
        {
            "course_id": int,
            "enrolled_date": str
        },
        ...
    ]
    """
    student_id = get_jwt_identity()
    enrollments = Enrollment.query.filter_by(student_id=int(student_id)).all()
    return jsonify([{
        "course_id": e.course_id,
        "enrolled_date": e.enrolled_date.isoformat() if e.enrolled_date else None
    } for e in enrollments]), 200



@routes.route('/assignments', methods=['POST'], endpoint="create_assignments")
@role_required('instructor')
def create_assignment_instructor():
    """
    Create a new assignment. Endpoint: POST /assignments (Instructor only)
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

@routes.route('/assignments/<int:course_id>', methods=['GET'], endpoint="get_assignments")
@jwt_required()
def get_course_assignments(course_id):
    """
    Get assignments for a specific course. Endpoint: GET /assignments/<course_id>
    Response:
    [
        {
            "id": int,
            "title": str,
            "description": str,
            "due_date": str
        },
        ...
    ]
    """
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    return jsonify([{
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "due_date": a.due_date.isoformat() if a.due_date else None
    } for a in assignments]), 200


@routes.route('/grades', methods=['POST'], endpoint="create_grades")
@role_required('instructor')
def assign_grade_instructor():
    """
    Assign a grade to a student. Endpoint: POST /grades (Instructor only)
    Expects JSON:
    {
        "assignment_id": int,
        "student_id": int,
        "grade": str
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

@routes.route('/student/history', methods=['GET'], endpoint="student_history")
@role_required('student')
def get_student_course_history():
    """
    Get student course history. Endpoint: GET /student/history (Student only)
    Response:
    [
        {
            "course_name": str,
            "enrolled_date": str,
            "grade": str
        },
        ...
    ]
    """
    try:
        student_id = get_jwt_identity()
        query = db.session.query(
            Course.name.label("course_name"),
            Enrollment.enrolled_date,
            Grade.grade
        ).join(
            Enrollment, Enrollment.course_id == Course.id
        ).outerjoin(
            Grade, (Grade.student_id == Enrollment.student_id) &
                   (Grade.assignment_id.in_(
                       db.session.query(Assignment.id).filter(
                           Assignment.course_id == Course.id)
                   ))
        ).filter(
            Enrollment.student_id == int(student_id)
        )

        result = query.all()
        history = [{
            "course_name": record.course_name,
            "enrolled_date": record.enrolled_date.isoformat() if record.enrolled_date else None,
            "grade": record.grade
        } for record in result]
        return jsonify(history), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching history: {e}")
        return jsonify({"message": "Error fetching history", "error": str(e)}), 500