import logging
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# uvicornのロガーを取得
LOGGER = logging.getLogger("uvicorn")


class RequestResponseLoggerMiddleware(BaseHTTPMiddleware):
    """
    リクエストとレスポンスをロギングするミドルウェア。

    Attributes:
        app (FastAPI): FastAPIアプリケーションインスタンス。
        log_request_body (bool): リクエストボディをログに含めるか。
        log_response_body (bool): レスポンスボディをログに含めるか。
    """

    def __init__(self, app: FastAPI, log_request_body: bool = True, log_response_body: bool = True):
        """
        RequestResponseLoggerMiddlewareを初期化する。

        Args:
            app (FastAPI): FastAPIアプリケーションインスタンス。
            log_request_body (bool): リクエストボディをログに含めるか。
            log_response_body (bool): レスポンスボディをログに含めるか。
        """
        LOGGER.info("RequestResponseLoggerMiddleware 初期化")
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        LOGGER.info(
            " ".join(
                [
                    "RequestResponseLoggerMiddleware initialized",
                    f"with log_request_body={self.log_request_body},",
                    f"log_response_body={self.log_response_body}",
                ]
            )
        )

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        リクエストとレスポンスをロギングする。

        Args:
            request (Request): リクエストオブジェクト。
            call_next (Callable[[Request], Awaitable[Response]]): 次のミドルウェアやエンドポイントを呼び出す関数。

        Returns:
            Response: 処理されたレスポンスオブジェクト。
        """
        LOGGER.info("RequestResponseLoggerMiddleware dispatch開始")

        # リクエストのログ記録
        await self._log_request(request)

        # レスポンスの処理
        response = await call_next(request)

        # レスポンスのログ記録
        response = await self._log_response(response)

        return response

    async def _log_request(self, request: Request) -> None:
        """
        リクエストの詳細をロギングする。

        Args:
            request (Request): ログに記録するリクエストオブジェクト。
        """
        LOGGER.info(f"Request URL: {request.url}")
        LOGGER.info(f"Request method: {request.method}")
        LOGGER.info(f"Request headers: {dict(request.headers)}")
        if self.log_request_body:
            body = await request.body()
            LOGGER.info(f"Request body: {body.decode('utf-8') if body else 'No Body'}")

    async def _log_response(self, response: Response) -> Response:
        """
        レスポンスの詳細をロギングする。

        Args:
            response (Response): ログに記録するレスポンスオブジェクト。

        Returns:
            Response: 再構築されたレスポンスオブジェクト。
        """
        LOGGER.info(f"Response status code: {response.status_code}")

        # レスポンスボディの取得と再構築
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        response.body_iterator = iter([response_body])  # 再利用のためにボディを再構築

        if self.log_response_body:
            try:
                LOGGER.info(f"Response body: {response_body.decode('utf-8')}")
            except UnicodeDecodeError:
                LOGGER.warning("Response body could not be decoded.")

        # 再構築されたレスポンスを返す
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
