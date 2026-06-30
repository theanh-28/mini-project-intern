import logging

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from datetime import datetime, timezone

from app.schemas.auth import LoginRequest, LoginResponse
from app.db.session import get_db
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.core.security import create_access_token


auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = LoginRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    
    db = get_db()

    user_service = UserService(UserRepository(db))

    user, error = user_service.auth_user(data.email, data.password)

    if not user:
        return jsonify({'error': error}), 401
    
    if not user.is_active:
        return jsonify({'error': "Tài khoản đang bị khóa"}), 403

    user.last_login = datetime.now()
    db.commit()

    access_token = create_access_token(user.user_id, user.is_admin)
    logger.info("User logged in: id=%s, is_admin=%s", user.user_id, user.is_admin)

    response_data = LoginResponse(access_token=access_token, is_admin=user.is_admin)
    return jsonify(response_data.model_dump()), 200




         

