import logging

from fastapi import APIRouter, Depends, HTTPException  # noqa: F401
from fastapi.security import APIKeyHeader  # noqa: F401
from fastapi_versioning import version  # noqa: F401
from sqlalchemy.orm import Session  # noqa: F401

from app_state import environment_info_static
from commons.environment_master_key import EnvironmentMasterKey

# uvicornのロガー設定（共通）
LOGGER = logging.getLogger("uvicorn")

# 共通のAPIキー定義
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


def extract_token(authorization: str) -> str:
    """
    AuthorizationヘッダーからBearerトークンを抽出します。

    Args:
        authorization (str): Authorizationヘッダーの値。

    Returns:
        str: Bearerトークン。

    Raises:
        HTTPException: Authorizationヘッダーがない、または無効な場合。
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    return authorization.replace("Bearer ", "")


def create_router(prefix: str, tags: list[str]) -> APIRouter:
    """
    APIRouterを作成する共通関数。

    Args:
        prefix (str): エンドポイントの共通プレフィックス。
        tags (list[str]): ドキュメント用タグリスト。

    Returns:
        APIRouter: 設定済みのAPIRouterインスタンス。
    """
    return APIRouter(prefix=prefix, tags=tags)


def get_environment_info_static(key_code: EnvironmentMasterKey) -> str:
    """
    静的なenvironment_infoから指定したキーの値を取得する。

    Args:
        key_code (EnvironmentMasterKey): 取得するキーコード。

    Returns:
        str: 対応する環境情報の値。

    Raises:
        HTTPException: キーコードに対応する値が見つからない場合。
    """
    value = environment_info_static.get(key_code.value)
    if not value:
        LOGGER.error(f"Environment info not found for key_code: {key_code.value}")
        raise HTTPException(
            status_code=404,
            detail=f"Environment info not found for key_code: {key_code.value}",
        )
    return value["values"]


def handle_exception(e: Exception) -> HTTPException:
    """
    エラーハンドリングを共通化します。

    Args:
        e (Exception): 発生した例外。

    Returns:
        HTTPException: 対応するHTTPException。
    """
    if isinstance(e, HTTPException):
        LOGGER.error(f"HTTP error occurred: {e.detail}")
        raise e
    elif isinstance(e, ValueError):
        LOGGER.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
    elif isinstance(e, PermissionError):
        LOGGER.error(f"Permission error: {e}")
        raise HTTPException(status_code=403, detail=f"Permission denied: {e}")
    else:
        LOGGER.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
