# ローカルモジュール（例: プロジェクト内のモジュール）
import logging

from utils.firebase_auth import verify_firebase_token
from utils.protocol import (
    Depends,
    create_router,
    version,
)

# ルーター設定（共通関数を利用）
router = create_router(prefix="/users", tags=["users"])

# Uvicorn 用ロガー取得
LOGGER = logging.getLogger("uvicorn.routers.http")


@router.post("/")
@version(0, 1)
async def user(user_data: dict = Depends(verify_firebase_token)):
    """
    健康チェック用エンドポイント。

    Args:
        db (Session): データベースセッション（依存関係として注入）。

    Returns:FF
        dict: サービスのバージョン情報。
    """
    LOGGER.info(f"user_data: {user_data}")
    return {
        "message": "You are authenticated with Firebase!",
        "user_id": user_data["uid"],
        "email": user_data.get("email"),
    }
