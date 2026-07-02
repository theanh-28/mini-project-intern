import logging

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, LoginResponse
from app.services.user_service import get_user_service
from app.core.security import create_access_token


auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = LoginRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    
    user_service = get_user_service()
    user, error = user_service.auth_user(data.email, data.password)

    if not user:
        status_code = 403 if error == "Tài khoản đang bị khóa" else 401
        return jsonify({'error': error}), status_code

    access_token = create_access_token(user.user_id, user.is_admin)
    logger.info("User logged in: id=%s, is_admin=%s", user.user_id, user.is_admin)

    response_data = LoginResponse(access_token=access_token, is_admin=user.is_admin)
    return jsonify(response_data.model_dump()), 200
