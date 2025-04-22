#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import logging
import os
from typing import List

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from utils.protocol import handle_exception  # 共通例外処理

# Uvicorn 用ロガー取得
LOGGER = logging.getLogger("uvicorn.middleware_manager")


def include_all_middlewares(
    app: FastAPI,
    middlewares_pkg: str = "middlewares",
    skip_middlewares: List[str] = None,
) -> None:
    """
    指定パッケージ内のすべての BaseHTTPMiddleware サブクラスを
    FastAPI アプリに動的に登録します。

    Args:
        app (FastAPI): FastAPI アプリケーションインスタンス
        middlewares_pkg (str): ミドルウェアを格納するパッケージ名
        skip_middlewares (List[str]): 登録をスキップするミドルウェア名リスト

    Raises:
        HTTPException/ValueError: app が None の場合やインポートエラー
    """
    # app の検証
    if app is None:
        handle_exception(
            message="FastAPI アプリケーションが None です",
            exception=ValueError("app must not be None"),
        )

    # スキップリストのデフォルト設定
    if skip_middlewares is None:
        skip_middlewares = [
            "BaseHTTPMiddleware",
            "CorrelationIdMiddleware",
            "PyInstrumentProfilerMiddleware",
        ]

    try:
        pkg = importlib.import_module(middlewares_pkg)
    except Exception as e:
        handle_exception(
            message=f"ミドルウェアパッケージのインポートに失敗: {middlewares_pkg}",
            exception=e,
        )
    base_path = pkg.__path__[0]

    # ファイル走査
    for filename in os.listdir(base_path):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue
        module_name = f"{middlewares_pkg}.{filename[:-3]}"
        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            LOGGER.error(f"モジュール {module_name} のインポートエラー: {e}")
            continue

        # モジュール内のクラスを走査
        for attr_name in dir(module):
            cls = getattr(module, attr_name)
            # クラスかつ BaseHTTPMiddleware のサブクラス
            if (
                isinstance(cls, type)
                and issubclass(cls, BaseHTTPMiddleware)
                # 抽象クラス自体は登録しない
                and cls is not BaseHTTPMiddleware
                # スキップ対象は登録しない
                and cls.__name__ not in skip_middlewares
            ):
                # ミドルウェア登録
                try:
                    app.add_middleware(cls)
                    LOGGER.info(f"ミドルウェア {cls.__name__} を登録しました。")
                except Exception as e:
                    LOGGER.error(f"{cls.__name__} の登録に失敗: {e}")
