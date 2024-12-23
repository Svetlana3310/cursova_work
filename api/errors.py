from flask import jsonify
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized
from sqlalchemy.exc import IntegrityError

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        response.data = jsonify({
            "error": e.name,
            "message": e.description,
            "status_code": e.code
        }).data
        response.content_type = "application/json"
        return response

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return jsonify({
            "error": "Bad Request",
            "message": e.description,
            "status_code": 400
        }), 400

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(e):
        return jsonify({
            "error": "Unauthorized",
            "message": e.description,
            "status_code": 401
        }), 401

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e):
        return jsonify({
            "error": "Database Error",
            "message": "A database integrity error occurred.",
            "details": str(e),
            "status_code": 409
        }), 409

    @app.errorhandler(Exception)
    def handle_general_exception(e):
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e),
            "status_code": 500
        }), 500