from fastapi import Request, Response
from typing import Any
import httpx
import logging
import time

from app.clients.http_client import http_client
from app.gateway.context import ContextStore
from app.core.exceptions import UpstreamTimeout, UpstreamUnavailable, BadGateway

logger = logging.getLogger("gateway.proxy")

# Header không nên forward khi gửi request đi backend
REQUEST_HOP_BY_HOP_HEADERS = {
    "host",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "authorization",
}

# Header không nên forward khi trả response về lại client
RESPONSE_EXCLUDED_HEADERS={
    "content-length",
    "content-encoding",
    "transfer-encoding",
    "connection",
}

async def reverse_proxy(target_url: str, request: Request) -> Response:
    headers = _clean_request_headers(request)
    headers = _inject_context_headers(headers)
    
    body = await request.body()

    try:
        start = time.time()
        logger.info(f"-> {request.method} {target_url}")

        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=body,
            timeout=30.0
        )

        response_headers = {k: v for k, v in response.headers.items() if k.lower() not in RESPONSE_EXCLUDED_HEADERS}

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers
        )
    except httpx.TimeoutException:
        duration_ms = (time.time() - start) * 1000
        logger.error(f"<- TIMEOUT {target_url} ({duration_ms:.1f}ms)")
        raise UpstreamTimeout()

    except httpx.ConnectError:
        duration_ms = (time.time() - start) * 1000
        logger.error(f"<- CONNECT_ERROR {target_url} ({duration_ms:.1f}ms)")
        raise UpstreamUnavailable()

    except httpx.NetworkError as e:
        duration_ms = (time.time() - start) * 1000
        logger.error(f"<- NETWORK_ERROR {target_url}: {e} ({duration_ms:.1f}ms)")
        raise BadGateway(message=f"Lỗi cổng kết nối (Network error): {e}")

    except httpx.HTTPError as e:
        duration_ms = (time.time() - start) * 1000
        logger.error(f"<- UNEXPECTED_ERROR {target_url}: {e} ({duration_ms:.1f}ms)", exc_info=True)
        raise BadGateway()



def _serialize_header_value(value: Any) -> str:
    """
    serialize giá trị trong user_info
    """
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (list, tuple)):
        return ",".join(str(v) for v in value)
    if value is None:
        return ""
    return str(value)

def _clean_request_headers(request: Request) -> dict:
    """
    Loại bỏ hop-by-hop headers, giữ lại phần còn lại để forward đi backend.
    """

    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in REQUEST_HOP_BY_HOP_HEADERS
    }
    return headers

def _inject_context_headers(headers: dict) -> dict:
    """
    Gắn thêm thông tin từ ContextStore vào headers forward đi backend.
    """

    headers["X-User-Id"] = str(ContextStore.get_user_id() or "")
    headers["X-Correlation-ID"] = str(ContextStore.get_correlation_id() or "")

    user_info = ContextStore.get_user_info()
    if user_info:
        for key, value in user_info.items():
            header_name = f"X-User-{key.replace('_', '-').title()}"
            headers[header_name] = _serialize_header_value(value)

    return headers