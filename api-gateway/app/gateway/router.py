from fastapi import Request, Response, APIRouter

from app.core.config import settings
from app.gateway.proxy import reverse_proxy
from app.plugins.auth_plugin import authenticate_request
from app.core.exceptions import RouteNotFoundError

router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_catch_all(path: str, request: Request) -> Response:
    """
    Catch-all route để điều phối tất cả request qua API Gateway.
    Nếu path không nằm trong router_map sẽ ném lỗi RouteNotFoundError (404).
    """
    req_path = f"/{path}"
    target_service_url = None

    # Tìm kiếm prefix tương ứng trong bản đồ định tuyến
    for prefix, target_base in settings.router_map.items():
        if req_path.startswith(prefix):
            target_service_url = target_base
            break

    # Nếu không khớp với bất kỳ tuyến đường nào, trả về lỗi 404 Route Not Found
    if not target_service_url:
        raise RouteNotFoundError()

    # Thực hiện plugin xác thực cho các route cần bảo mật
    await authenticate_request(request)

    # Xây dựng URL đầy đủ để chuyển tiếp sang backend
    target_url = f"{target_service_url.rstrip('/')}{req_path}"

    # Thực hiện forward request qua Reverse Proxy
    return await reverse_proxy(target_url, request)