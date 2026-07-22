import logging
from fastapi import Request

from app.core.config import settings
from app.gateway.context import ContextStore
from app.core.exceptions import InvalidTokenError
from app.services.auth_service import AuthService

logger = logging.getLogger("gateway.auth")

PUBLIC_ROUTES = [
    "/",
    "/docs/",
    "/openapi.json",
    "/auth/login",
]

async def authenticate_request(request: Request) -> None:
    """
    plugin xác thực JWT token
    """
    path = request.url.path
    if path in PUBLIC_ROUTES or any(path.startswith(route) for route in PUBLIC_ROUTES if route.endswith("/")):
        return

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header")
        raise InvalidTokenError("Yêu cầu không có token xác thực")
    
    token = auth_header.split(" ")[1]
    payload = AuthService.verify_token(token)

    ContextStore.set_user_id(int(payload.get("sub")) if payload.get("sub") else None)
    ContextStore.set_user_info({
        "is_admin": payload.get("is_admin")
    })

    
