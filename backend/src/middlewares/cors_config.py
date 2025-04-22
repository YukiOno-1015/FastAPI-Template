#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CORS ミドルウェア設定モジュール

環境変数:
  CORS_ALLOW_ORIGINS     許可するオリジン (カンマ区切り、デフォルト: "*")
  CORS_ALLOW_METHODS     許可する HTTP メソッド (カンマ区切り、デフォルト: "*")
  CORS_ALLOW_HEADERS     許可するヘッダー (カンマ区切り、デフォルト: "*")
  CORS_ALLOW_CREDENTIALS クッキー等の送信を許可 (true/false、デフォルト: "true")
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Uvicorn 用ロガーを取得
LOGGER = logging.getLogger("uvicorn.middleware.cors")


class CORSConfig:
    """
    FastAPI アプリケーションに CORS ミドルウェアを追加するクラス。

    コンストラクタ実行時に以下の環境変数を読み込み、設定を適用します。
      - CORS_ALLOW_ORIGINS
      - CORS_ALLOW_METHODS
      - CORS_ALLOW_HEADERS
      - CORS_ALLOW_CREDENTIALS
    """

    def __init__(self, app: FastAPI):
        # 環境変数から設定値を取得（デフォルトは全許可）
        origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
        methods = os.getenv("CORS_ALLOW_METHODS", "*")
        headers = os.getenv("CORS_ALLOW_HEADERS", "*")
        credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower()

        allow_origins = origins.split(",") if origins != "*" else ["*"]
        allow_methods = methods.split(",") if methods != "*" else ["*"]
        allow_headers = headers.split(",") if headers != "*" else ["*"]
        allow_credentials = credentials == "true"

        LOGGER.info(
            "[CORSConfig] 設定を読み込み: "
            f"origins={allow_origins}, methods={allow_methods}, "
            f"headers={allow_headers}, credentials={allow_credentials}"
        )

        # ミドルウェアの追加
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
            allow_credentials=allow_credentials,
        )
