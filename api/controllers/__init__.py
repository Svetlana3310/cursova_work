from .user_controller import user_bp
from .course_controller import course_bp
from .enrollment_controller import enrollment_bp
from .assignment_controller import assignment_bp
from .grade_controller import grade_bp
from .auth_controller import auth_bp
from .analytics import analytics_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(course_bp, url_prefix='/courses')
    app.register_blueprint(enrollment_bp, url_prefix='/enrollments')
    app.register_blueprint(assignment_bp, url_prefix='/assignments')
    app.register_blueprint(grade_bp, url_prefix='/grades')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
