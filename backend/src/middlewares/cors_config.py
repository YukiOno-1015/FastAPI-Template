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
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from commons.settings import settings

# Uvicorn 用ロガーを取得
LOGGER = logging.getLogger("uvicorn.middleware.cors")


class CORSConfig:
    """
    FastAPI アプリケーションに CORS ミドルウェアを追加するクラス。

    Settings.cors_allow_* をカンマで分割してリスト化し、
      - CORS_ALLOW_ORIGINS
      - CORS_ALLOW_METHODS
      - CORS_ALLOW_HEADERS
      - CORS_ALLOW_CREDENTIALS
    """

    def __init__(self, app: FastAPI):
        # カンマ区切りの文字列をリストに変換。"*" はワイルドカードとして扱う
        def to_list(val: Optional[str]) -> list[str]:
            if not val or val.strip() == "*":
                return ["*"]
            return [v.strip() for v in val.split(",") if v.strip()]

        allow_origins = to_list(settings.cors_allow_origins)
        allow_methods = to_list(settings.cors_allow_methods)
        allow_headers = to_list(settings.cors_allow_headers)
        allow_credentials = settings.cors_allow_credentials

        LOGGER.info(
            f"[CORSConfig] settings から読み込み: "
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
