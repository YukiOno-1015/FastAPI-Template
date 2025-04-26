# -*- coding: utf-8 -*-
"""
ルーター自動登録モジュール

このモジュールは指定されたパッケージ以下を再帰的にスキャンし、
`router` 属性を持つすべてのサブモジュールを FastAPI に自動登録します。

機能:
 1. `pkgutil.walk_packages` による再帰スキャン
 2. 除外パッケージ・ディレクトリのフィルタリング
 3. モジュール単位で `router` 属性を検出
 4. HTTP ルート (`APIRoute`) と WebSocket ルート (`WebSocketRoute`) の分離登録
"""
import importlib
import logging
import pkgutil
from typing import List, Set

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.routing import WebSocketRoute

# Uvicorn 用ロガー取得
LOGGER = logging.getLogger("uvicorn.routers_manager")

# スキャン対象から除外するパッケージ／ディレクトリ名
EXCLUDED_DIRS: Set[str] = {
    "__pycache__",
    ".pytest_cache",
    "alembic",
    "utils",
    "static",
    "core",
    "middlewares",
    "schemas",
    "models",
    "commons",
    "repositories",
}


def include_all_routers(app: FastAPI, root_pkg: str = "routers") -> List[WebSocketRoute]:
    """
    指定パッケージ配下を再帰的にスキャンし、
    `router` 属性を持つ各モジュールから HTTP と WebSocket のルートを登録します。

    Args:
        app (FastAPI): FastAPI アプリケーションインスタンス
        root_pkg (str): ルートパッケージ名（例: 'routers'）
    """
    try:
        pkg = importlib.import_module(root_pkg)
    except ModuleNotFoundError:
        LOGGER.error(f"ルートパッケージ '{root_pkg}' が見つかりません。")
        return

    ws_routes = []
    # 再帰的にサブモジュールを検索
    for finder, module_name, is_pkg in pkgutil.walk_packages(pkg.__path__, prefix=f"{root_pkg}."):
        # 除外ディレクトリがパスに含まれる場合はスキップ
        if any(part in EXCLUDED_DIRS for part in module_name.split(".")):
            LOGGER.debug(f"スキップ (除外対象): {module_name}")
            continue

        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            LOGGER.error(f"モジュール {module_name} のインポートエラー: {e}", exc_info=True)
            continue

        router = getattr(module, "router", None)
        if not router:
            continue

        http_routes = []
        # ルートを HTTP と WebSocket に分割
        for route in router.routes:
            if isinstance(route, APIRoute):
                http_routes.append(route)
            elif isinstance(route, WebSocketRoute):
                # WebSocketRoute には methods 属性がないため空セットを設定
                setattr(route, "methods", set())
                ws_routes.append(route)
            else:
                http_routes.append(route)

        # HTTP ルートのみを登録用に設定
        router.routes = http_routes
        try:
            app.include_router(router)
            LOGGER.info(f"HTTP ルーター登録: {module_name}.router")
        except Exception as e:
            LOGGER.error(f"HTTP ルーター登録失敗: {module_name}.router - {e}")

    return ws_routes
