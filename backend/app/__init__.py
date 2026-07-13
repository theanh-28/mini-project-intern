from flask import Flask, g, jsonify
import uuid
import logging
from werkzeug.exceptions import HTTPException

from app.core.exceptions import AppException
from app.core.config import settings
from pydantic import ValidationError

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return '<h1>Hello, World!</h1>'
    
    # Cấu hình ứng dụng
    app.config['DEBUG'] = settings.debug

    # Đăng ký before_request 
    from app.core.hook import login_required
    
    app.before_request(login_required)


    # teardown db
    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop('db', None)
        if db is not None:
            if error:
                db.rollback()
            db.close()

    # Xử lý ngoại lệ AppException
    @app.errorhandler(AppException)
    def handle_app_exception(e):
        return jsonify({
            "error": e.message, 
            "code": e.code_error
            }), e.status_code

    # Xử lý lỗi validation Pydantic
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({
            "error": e.errors(),
            "code": "VALIDATION_ERROR"
        }), 400

    # Xử lý ngoại lệ HTTPException
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            "error": str(e.description),
            "code": e.name.upper().replace(" ", "_")
        }), e.code

    # Xử lý ngoại lệ bất ngờ
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        if isinstance(e, HTTPException):
            return handle_http_exception(e)

        error_id = str(uuid.uuid4())
        logger.exception(f"{error_id} Unhandled exception")
        return jsonify({
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "error_id": error_id
        }), 500


    # Đăng ký blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app