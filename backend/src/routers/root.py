import logging

from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlalchemy.orm import Session

from database.session import get_session
from services.environment_service import EnvironmentService

# uvicornのロガーを取得
LOGGER = logging.getLogger("uvicorn")

# ルーター設定
router = APIRouter(
    prefix="",  # URLのプレフィックス（このルーターに共通するURLのベースパス）
    tags=["index"],  # タグ（ドキュメントでのグループ化に使用）
)


@router.get("/reload")
@version(0, 1)
async def memory_reload(db: Session = Depends(get_session)):
    """
    環境情報を再読み込みするエンドポイント

    このエンドポイントは、EnvironmentServiceを使用して
    環境情報を再度データベースから取得し、静的情報を更新します。

    Parameters:
    - db: データベースセッション（依存関係として注入）

    Returns:
    - dict: 操作結果のメッセージを返します。
    """
    # データベースセッションを使用して EnvironmentService を初期化
    environment_service = EnvironmentService(db=db)
    environment_service.update_environment_info_static()  # 静的な環境情報を更新
    return {"message": "OK"}  # 成功メッセージを返す


@router.get("/healthcheck")
@version(0, 1)
async def healthcheck(db: Session = Depends(get_session)):
    """
    健康チェック用エンドポイント

    このエンドポイントは、EnvironmentServiceを使用して特定の環境情報を取得し、
    サービスのバージョン情報を返します。

    Parameters:
    - db: データベースセッション（依存関係として注入）

    Returns:
    - dict: サービスのバージョン情報
    """
    # データベースセッションを使用して EnvironmentService を初期化
    environment_service = EnvironmentService(db=db)

    # 環境情報を取得（例としてkey_codeは"10000002"を指定）
    environment_info = environment_service.get_environment_info_static(key_code="10000002")

    # ロガーに環境情報を出力
    LOGGER.info(f"Environment info: {environment_info}")

    # 取得した環境情報からバージョン情報を返す
    return {"version": environment_info.get("values", "unknown")}
