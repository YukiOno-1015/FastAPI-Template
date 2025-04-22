#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from fastapi_versioning import VersionedFastAPI
from sqlmodel import Session

from app_state import environment_info_static
from database.connection import engine
from middlewares.cors_config import CORSConfig
from middlewares.header_middleware import HeaderMiddleware
from repositories.environment_repository import EnvironmentRepository
from services.environment_service import EnvironmentService
from utils.middlewares_manager import include_all_middlewares
from utils.routers_manager import include_all_routers

# Uvicornの標準ロガーを取得
LOGGER = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクル管理:
    - 起動時にDB初期化
    - シャットダウン時のクリーンアップ
    """
    LOGGER.info("[LIFECYCLE] アプリ起動開始")
    try:
        initialize_database()
        LOGGER.info("[LIFECYCLE] 初期化完了")
        yield
    except Exception:
        LOGGER.error("[LIFECYCLE] 起動中に例外発生", exc_info=True)
        raise
    finally:
        LOGGER.info("[LIFECYCLE] シャットダウン処理開始")
        # TODO: 必要に応じてリソース解放処理を追加
        LOGGER.info("[LIFECYCLE] シャットダウン処理完了")


def create_app() -> FastAPI:
    """
    FastAPIアプリケーションを生成し、
    ミドルウェア・ルーター・バージョニング・静的配信を設定する。
    """
    # アプリケーションインスタンス生成

    app = FastAPI(
        title="FastAPI Template Updated",
        lifespan=lifespan,
        # root_path="/",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        description="FastAPI Template",
        version="0.0.1",
        # contact={"name": "FastAPI Template", "url": "", "email": ""},
        redirect_slashes=False,
    )

    LOGGER.info("[INIT] FastAPI インスタンス生成完了")

    # CORS設定
    LOGGER.info("[INIT] CORS設定開始")
    configure_cors(app)
    LOGGER.info("[INIT] CORS設定完了")

    # 共通ミドルウェア登録
    LOGGER.info("[INIT] ミドルウェア登録開始")
    include_all_middlewares(app)
    # HeaderMiddleware: ペイロード署名・ヘッダー管理
    app.add_middleware(HeaderMiddleware)
    LOGGER.info("[INIT] ミドルウェア登録完了")

    # ルーター登録
    LOGGER.info("[INIT] ルーター登録開始")
    include_all_routers(app, "./routers", "routers")
    LOGGER.info("[INIT] ルーター登録完了")
    # ページネーション
    LOGGER.info("[INIT] ページネーション設定開始")
    add_pagination(app)
    LOGGER.info("[INIT] ページネーション設定完了")

    # バージョニング
    LOGGER.info("[INIT] バージョニング設定開始")
    app = VersionedFastAPI(
        app,
        version_format="{major}_{minor}",
        prefix_format="/v{major}_{minor}",
        middleware=app.user_middleware,
        lifespan=app.router.lifespan_context,
        root_path=app.root_path,
        docs_url=app.docs_url,
        redoc_url=app.redoc_url,
        openapi_url=app.openapi_url,
        enable_latest=True,
        contact=app.contact,
    )
    LOGGER.info("[INIT] バージョニング設定完了")

    # 静的ファイル配信
    LOGGER.info("[INIT] 静的ファイル配信設定開始")
    app.mount("/static", StaticFiles(directory="./static"), name="static")
    LOGGER.info("[INIT] 静的ファイル配信設定完了")

    LOGGER.info("[INIT] アプリ初期化完了")
    return app


def configure_cors(app: FastAPI) -> None:
    """
    CORS設定関数:
    許可するオリジン・メソッド・ヘッダーを環境変数等で管理可能
    """
    LOGGER.info("[CORS] 設定開始")
    # CORSConfig にて環境変数を元に設定を適用
    CORSConfig(app)
    LOGGER.info("[CORS] 設定完了")


def initialize_database() -> None:
    """
    DB初期化関数:
    - テーブル生成
    - 環境情報をキャッシュにロード
    """
    LOGGER.info("[DB] 初期化処理開始")
    # セッション生成
    session = Session(engine)
    try:
        repo = EnvironmentRepository(db=session)
        service = EnvironmentService(repository=repo)
        service.refresh_cache()
        LOGGER.info(f"[DB] キャッシュ更新完了: {len(environment_info_static)} 件")
    except Exception as e:
        LOGGER.error(f"[DB] 初期化中にエラー発生: {e}", exc_info=True)
        raise
    finally:
        session.close()


# アプリ生成
app = create_app()
