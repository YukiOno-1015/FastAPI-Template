#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
アプリケーション起動モジュール

・FastAPI インスタンスの生成と各種設定
・CORS ミドルウェア（環境変数ベース）
・汎用ミドルウェア一括登録
・HeaderMiddleware（HMAC シグネチャ／不要ヘッダー削除）
・ルーター自動登録（DDD 構成対応）
・ページネーション／API バージョニング
・静的ファイル配信
・WebSocket チャットエンドポイント
"""

import logging
from contextlib import asynccontextmanager

import anyio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from fastapi_versioning import VersionedFastAPI
from sqlmodel import Session

from app_state import environment_info_static
from commons.settings import settings
from database.connection import engine
from middlewares.cors_config import CORSConfig
from middlewares.header_middleware import HeaderMiddleware
from repositories.environment_repository import EnvironmentRepository
from services.environment_service import EnvironmentService
from utils.middlewares_manager import include_all_middlewares
from utils.routers_manager import include_all_routers

# Uvicorn ロガー取得
LOGGER = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションの起動とシャットダウンの処理。
    """
    LOGGER.info("[LIFECYCLE] アプリ起動開始")
    try:
        # ブロッキング処理を別スレッドで実行
        await anyio.to_thread.run_sync(initialize_database)
        LOGGER.info("[LIFECYCLE] 初期化完了")
        yield
    except Exception:
        LOGGER.error("[LIFECYCLE] 起動中に例外発生", exc_info=True)
        raise
    finally:
        LOGGER.info("[LIFECYCLE] シャットダウン処理開始")
        # TODO: リソース解放など
        LOGGER.info("[LIFECYCLE] シャットダウン処理完了")


def create_app() -> FastAPI:
    """
    FastAPI アプリケーションインスタンスの生成と設定適用。
    """
    app = FastAPI(
        title=settings.title,
        version=settings.version,
        description=settings.description,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
        redirect_slashes=settings.redirect_slashes,
    )
    LOGGER.info("[INIT] FastAPI インスタンス生成完了")

    # CORS ミドルウェア設定
    LOGGER.info("[INIT] CORS 設定開始")
    CORSConfig(app)
    LOGGER.info("[INIT] CORS 設定完了")

    # 共通ミドルウェア登録
    LOGGER.info("[INIT] 共通ミドルウェア登録開始")
    include_all_middlewares(app)
    # HMAC シグネチャ＆不要ヘッダー管理
    app.add_middleware(HeaderMiddleware)
    LOGGER.info("[INIT] ミドルウェア登録完了")

    # ページネーション
    LOGGER.info("[INIT] ページネーション設定開始")
    add_pagination(app)
    LOGGER.info("[INIT] ページネーション設定完了")

    # ルーター自動登録 (routers パッケージ)
    LOGGER.info("[INIT] ルーター登録開始")
    ws_routes = include_all_routers(app, root_pkg="routers")
    LOGGER.info("[INIT] ルーター登録完了")

    # API バージョニング
    LOGGER.info("[INIT] バージョニング設定開始")
    versioned_app = VersionedFastAPI(
        app,
        version_format="{major}_{minor}",
        prefix_format="/v{major}_{minor}",
        middleware=app.user_middleware,
        lifespan=app.router.lifespan_context,
        enable_latest=True,
    )
    LOGGER.info("[INIT] バージョニング設定完了")

    # 静的ファイル配信
    LOGGER.info("[INIT] 静的ファイル配信設定開始")
    versioned_app.mount("/static", StaticFiles(directory="./static"), name="static")
    LOGGER.info("[INIT] 静的ファイル配信設定完了")

    # 7) バージョニング後に WebSocketRoute を追加
    for ws in ws_routes:
        versioned_app.router.routes.append(ws)
        LOGGER.info(f"WebSocket ルーター登録（バージョニング後）: {ws.path}")
    return versioned_app


def initialize_database() -> None:
    """
    DB 初期化:
      - テーブル作成
      - 環境情報キャッシュロード
    """
    LOGGER.info("[DB] 初期化処理開始")
    session = Session(engine)
    try:
        repo = EnvironmentRepository(db=session)
        service = EnvironmentService(repository=repo)
        service.refresh_cache()
        LOGGER.info(f"[DB] キャッシュ更新完了: {len(environment_info_static)} 件")
    except Exception:
        LOGGER.error("[DB] 初期化中にエラー発生", exc_info=True)
        raise
    finally:
        session.close()


# アプリ生成
app = create_app()
