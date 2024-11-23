import logging

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

# uvicornのロガーを取得
LOGGER = logging.getLogger("uvicorn")


class RemoveHeadersMiddleware(BaseHTTPMiddleware):
    """
    レスポンスから特定のヘッダーを削除するミドルウェア。

    Attributes:
        app (FastAPI): FastAPIアプリケーションインスタンス。
        headers_to_remove (list[str]): 削除するヘッダーのリスト。デフォルトは ["X-Uvicorn", "Server"]。
    """

    def __init__(self, app: FastAPI, headers_to_remove: list[str] = None):
        """
        RemoveHeadersMiddlewareを初期化する。

        Args:
            app (FastAPI): FastAPIアプリケーションインスタンス。
            headers_to_remove (list[str]): 削除するヘッダーのリスト。
        """
        LOGGER.info("RemoveHeadersMiddleware 初期化")
        super().__init__(app)
        self.headers_to_remove = headers_to_remove or ["X-Uvicorn", "Server"]  # デフォルト: X-Uvicorn, Server
        LOGGER.info(f"RemoveHeadersMiddleware initialized with headers: {self.headers_to_remove}")

    async def dispatch(self, request: Request, call_next):
        """
        リクエストを処理し、指定されたヘッダーを削除したレスポンスを返す。

        Args:
            request (Request): リクエストオブジェクト。
            call_next (Callable): 次のミドルウェアやエンドポイントを呼び出す関数。

        Returns:
            Response: ヘッダーが削除されたレスポンスオブジェクト。
        """
        LOGGER.info("RemoveHeadersMiddleware dispatch開始")
        response = await call_next(request)

        # 指定されたヘッダーを削除
        for header in self.headers_to_remove:
            if header in response.headers:
                del response.headers[header]
                LOGGER.info(f"{header} ヘッダーが削除されました")

        return response
