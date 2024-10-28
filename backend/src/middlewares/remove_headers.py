from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RemoveHeadersMiddleware(BaseHTTPMiddleware):
    """
    レスポンスから特定のヘッダーを削除するミドルウェア。
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Uvicornバージョン情報を削除
        if "X-Uvicorn" in response.headers:
            del response.headers["X-Uvicorn"]
        # Server情報を削除
        if "Server" in response.headers:
            del response.headers["Server"]
        return response
