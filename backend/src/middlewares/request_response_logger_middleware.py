#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Uvicorn用ロガーを取得
LOGGER = logging.getLogger("uvicorn.middleware.logger")


class RequestResponseLoggerMiddleware(BaseHTTPMiddleware):
    """
    リクエストおよびレスポンスを詳細に記録するミドルウェア。

    - リクエスト: method, URL, headers, body (オプション)
    - レスポンス: status_code, headers, body (オプション)
    """

    def __init__(self, app: FastAPI, log_request_body: bool = True, log_response_body: bool = True):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        LOGGER.info(
            f"RequestResponseLoggerMiddleware initialized "
            f"with log_request_body={self.log_request_body}, "
            f"log_response_body={self.log_response_body}"
        )

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # リクエスト内容をログ出力
        LOGGER.info(f"[Request] {request.method} {request.url}")
        LOGGER.info(f"[Request Headers] {dict(request.headers)}")
        if self.log_request_body:
            try:
                body = await request.body()
                LOGGER.info(f"[Request Body] {body.decode('utf-8')}")
            except Exception as e:
                LOGGER.warning(f"リクエストボディのログ取得時エラー: {e}")

        # レスポンス取得
        response = await call_next(request)

        # レスポンスボディを収集
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk

        # レスポンス情報をログ出力
        LOGGER.info(f"[Response] status_code={response.status_code}")
        if self.log_response_body:
            try:
                LOGGER.debug(f"[Response Body] {resp_body.decode('utf-8')}")
            except Exception:
                LOGGER.warning("レスポンスボディのデコードに失敗しました")

        # 新しい Response を構築して返却
        new_response = Response(
            content=resp_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
        return new_response
