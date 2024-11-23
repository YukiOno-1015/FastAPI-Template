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
from services.environment_service import EnvironmentService
from utils.middlewares_manager import include_all_middlewares
from utils.routers_manager import include_all_routers

# uvicornのロガーを使用
LOGGER = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクルイベントハンドラ。
    アプリケーションの起動時とシャットダウン時に処理を実行。
    """
    LOGGER.info("アプリケーションの起動開始")
    try:
        await initialize_database()
        LOGGER.info("アプリケーションの起動完了")
        yield  # アプリケーション稼働中はここで一時停止
    except Exception as e:
        LOGGER.error(f"アプリケーションの起動中にエラーが発生しました: {e}", exc_info=True)
        raise
    finally:
        LOGGER.info("アプリケーションのシャットダウン開始")
        # シャットダウン処理
        LOGGER.info("アプリケーションのシャットダウン完了")


def create_app() -> FastAPI:
    """
    FastAPIアプリケーションを作成し、ミドルウェアやルーターを設定する。

    Returns:
        FastAPI: 設定済みのFastAPIアプリケーションインスタンス。
    """
    LOGGER.info("FastAPIアプリケーションの初期化開始")
    app = FastAPI(
        lifespan=lifespan,
    )

    configure_cors(app)

    # ルーターとミドルウェアの設定
    include_all_routers(app)
    include_all_middlewares(app)

    # ページネーションを追加し、バージョン管理を適用
    add_pagination(app)
    app = VersionedFastAPI(
        app,
        middleware=app.user_middleware,  # ミドルウェアを引き継ぐ
        lifespan=app.router.lifespan_context,  # lifespanを引き継ぐ
    )

    LOGGER.info(f"VersionedFastAPI Middleware: {app.user_middleware}")
    app.mount("", StaticFiles(directory="./static"), name="static")
    LOGGER.info("FastAPIアプリケーションの初期化完了")
    return app


def configure_cors(app: FastAPI) -> None:
    """
    CORSの設定を行う。

    Args:
        app (FastAPI): FastAPIアプリケーションインスタンス。
    """
    LOGGER.info("CORS設定の構成中")
    CORSConfig(
        app,
        allow_origins=[
            "http://localhost",
            "https://localhost",
            "https://script.google.com",
            "http://localhost:8000",
            "http://sk4869.info",
            "https://sk4869.info",
            "http://sk4869.info/",
            "https://sk4869.info/",
        ],
    )
    LOGGER.info("CORS設定の構成完了")


async def initialize_database() -> None:
    """
    データベースのテーブルを作成し、EnvironmentInfoの情報を
    データベースから取得して静的変数に格納する。
    """
    LOGGER.info("データベースの初期化開始")
    try:
        with Session(engine) as session:
            service = EnvironmentService(db=session)
            service.update_environment_info_static()
        LOGGER.info(f"Loaded EnvironmentInfo Size: {len(environment_info_static)}")
    except Exception as e:
        LOGGER.error(f"データベースの初期化中にエラーが発生しました: {e}", exc_info=True)
        raise
    LOGGER.info("データベースの初期化完了")


# アプリケーションインスタンスの作成
app = create_app()
