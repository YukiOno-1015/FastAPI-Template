import logging
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from fastapi_versioning import VersionedFastAPI
from sqlmodel import SQLModel, Session
from database.connection import engine
from database.session import get_session
from app_state import environment_info_static
from services.environment_service import EnvironmentService
from middlewares.cors_config import CORSConfig
from utils.routers_manager import include_all_routers
from utils.middlewares_manager import include_all_middlewares

# uvicornのロガーを取得
LOGGER = logging.getLogger("uvicorn")

app = FastAPI()

CORSConfig(app)
include_all_middlewares(app)  # ミドルウェアを設定
include_all_routers(app)  # すべてのルーターをインク

app = add_pagination(app)
app = VersionedFastAPI(app)


def initialize_database() -> None:
    """
    データベースのテーブルを作成し、EnvironmentInfoの情報を
    データベースから取得して静的変数に格納します。

    Returns:
        None
    """
    try:
        SQLModel.metadata.create_all(bind=engine)
        LOGGER.info("データベースのテーブルを作成しました。")

        # セッションを管理して環境情報サービスを初期化
        with Session(engine) as session:
            service = EnvironmentService(db=session)
            service.update_environment_info_static()

        LOGGER.info(f"Loaded EnvironmentInfo Size: {len(environment_info_static)}")
    except Exception as e:
        LOGGER.error(f"データベースの初期化中にエラーが発生しました: {e}")
        raise


@app.on_event("startup")
async def on_startup() -> None:
    """
    アプリケーションの起動時に実行されるイベント。
    """
    initialize_database()  # 環境情報の初期化
