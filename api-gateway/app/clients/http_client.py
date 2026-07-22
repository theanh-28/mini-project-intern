import httpx

http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(
        connect=5.0,   # thời gian tối đa để MỞ kết nối TCP tới backend
        read=30.0,     # thời gian tối đa CHỜ backend trả response
        write=10.0,    # thời gian tối đa để GỬI dữ liệu (request body)
        pool=5.0,      # thời gian tối đa CHỜ có connection rảnh trong pool
    ),
    limits=httpx.Limits(
        max_connections=100,           # tổng số connection tối đa (tới mọi host)
        max_keepalive_connections=20,  # số connection giữ để tái sử dụng
        keepalive_expiry=5.0,          # giây — connection idle bao lâu thì bị đóng
    )
)

async def close_http_client():
    await http_client.aclose()