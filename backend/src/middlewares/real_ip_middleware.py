import logging

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

# uvicornのロガーを取得
LOGGER = logging.getLogger("uvicorn")


class RealIPMiddleware(BaseHTTPMiddleware):
    """
    リクエストのヘッダーからクライアントのリアルIPを取得して設定するミドルウェア。

    Attributes:
        app (FastAPI): FastAPIアプリケーションインスタンス。
        headers_to_check (list[str]): クライアントIPを取得するためのヘッダーリスト。
    """

    def __init__(self, app: FastAPI, headers_to_check: list[str] = None):
        """
        RealIPMiddlewareを初期化する。

        Args:
            app (FastAPI): FastAPIアプリケーションインスタンス。
            headers_to_check (list[str]): クライアントIPを取得するためのヘッダーリスト。
        """
        LOGGER.info("RealIPMiddleware 初期化")
        super().__init__(app)
        self.headers_to_check = headers_to_check or ["X-Forwarded-For", "CF-Connecting-IP", "True-Client-IP"]
        LOGGER.info(f"RealIPMiddleware initialized with headers: {self.headers_to_check}")

    async def dispatch(self, request: Request, call_next):
        """
        リクエストを処理し、クライアントのリアルIPをリクエストオブジェクトに設定する。

        Args:
            request (Request): リクエストオブジェクト。
            call_next (Callable): 次のミドルウェアやエンドポイントを呼び出す関数。

        Returns:
            Response: 処理されたレスポンスオブジェクト。
        """
        LOGGER.info("RealIPMiddleware dispatch開始")

        # ヘッダーからクライアントIPを取得
        client_ip = self._get_real_ip(request)
        if client_ip:
            LOGGER.info(f"クライアントのリアルIPを取得しました: {client_ip}")
            # クライアントIPをリクエストオブジェクトに設定
            request.scope["client"] = (client_ip, request.client.port)
        else:
            LOGGER.warning("リアルIPが取得できませんでした")

        response = await call_next(request)
        return response

    def _get_real_ip(self, request: Request) -> str:
        """
        リクエストヘッダーを解析してクライアントのリアルIPを取得する。

        Args:
            request (Request): リクエストオブジェクト。

        Returns:
            str: クライアントのリアルIPアドレス。取得できない場合は空文字列。
        """
        for header in self.headers_to_check:
            header_value = request.headers.get(header)
            if header_value:
                # ヘッダーがカンマ区切りの場合、最初のIPを取得
                real_ip = header_value.split(",")[0].strip()
                return real_ip
        return request.client.host  # ヘッダーがない場合はデフォルトでリクエスト元IPを使用
