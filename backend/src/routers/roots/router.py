# routers/router.py
# APIRouterを生成する共通ユーティリティを使用し、環境情報リロードとヘルスチェックを提供するエンドポイント定義
import logging

from commons.environment_master_key import EnvironmentMasterKey
from database.session import get_session
from repositories.environment_repository import EnvironmentRepository
from services.environment_service import EnvironmentService
from utils.protocol import Depends, Session, create_router, get_environment_info_static, version

# Uvicornロガーを使用
LOGGER = logging.getLogger("uvicorn.routers")

# ルーターの生成: ベースパス ''、タグ 'index'
router = create_router(prefix="", tags=["index"])


@router.get("/reload")
@version(0, 1)
async def memory_reload(db: Session = Depends(get_session)):
    """
    環境情報キャッシュをDBから再読み込みします。

    Args:
        db (Session): データベースセッション (依存注入)

    Returns:
        dict: 実行結果メッセージ
    """
    # リポジトリとサービスを生成し、キャッシュを更新
    repo = EnvironmentRepository(db=db)
    service = EnvironmentService(repository=repo)
    service.refresh_cache()

    LOGGER.info("[Router] Environment cache reloaded")
    return {"message": "Environment cache reloaded successfully"}


@router.get("/healthcheck")
@version(0, 1)
async def healthcheck():
    """
    サービスの健康状態を確認し、バージョン情報を返します。

    Returns:
        dict: キー 'version' に環境設定のバージョン値を含む
    """
    # プロトコルユーティリティ経由で環境情報を取得
    version_value = get_environment_info_static(EnvironmentMasterKey.VERSION)
    LOGGER.info(f"[Router] Healthcheck version: {version_value}")
    return {"version": version_value}
