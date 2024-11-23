# ローカルモジュール（例: プロジェクト内のモジュール）
from database.session import get_session
from routers.protocol import (
    LOGGER,
    Depends,
    EnvironmentMasterKey,
    Session,
    create_router,
    get_environment_info_static,
    version,
)
from services.environment_service import EnvironmentService

# ルーター設定（共通関数を利用）
router = create_router(prefix="", tags=["index"])


@router.get("/reload")
@version(0, 1)
async def memory_reload(db: Session = Depends(get_session)):
    """
    環境情報を再読み込みするエンドポイント。

    Args:
        db (Session): データベースセッション（依存関係として注入）。

    Returns:
        dict: 操作結果のメッセージを返します。
    """
    # EnvironmentServiceを初期化して環境情報を更新
    environment_service = EnvironmentService(db=db)
    environment_service.update_environment_info_static()

    return {"message": "OK"}  # 成功メッセージを返す


@router.get("/healthcheck")
@version(0, 1)
async def healthcheck():
    """
    健康チェック用エンドポイント。

    Args:
        db (Session): データベースセッション（依存関係として注入）。

    Returns:
        dict: サービスのバージョン情報。
    """
    version: str = get_environment_info_static(key_code=EnvironmentMasterKey.VERSION)
    LOGGER.info(f"version: {version}")
    # 取得した環境情報からバージョン情報を返す
    return {"version": version}
