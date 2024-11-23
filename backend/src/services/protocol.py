import logging
from datetime import date, datetime, timedelta  # noqa: F401
from typing import Any  # noqa: F401

from fastapi import HTTPException

from app_state import environment_info_static
from commons.environment_master_key import EnvironmentMasterKey  # noqa: F401

# ロガーの設定
LOGGER = logging.getLogger("uvicorn")


def get_environment_value(key_code: str) -> str:
    """環境変数から値を取得"""
    value: dict[str, str] | None = environment_info_static.get(key_code)
    if not value:
        handle_exception("環境設定の値が見つかりません", KeyError(f"Key '{key_code}' not found in environment info."))
    return value["values"]


def handle_exception(message: str, exception: Exception) -> None:
    """エラー処理を行い、HTTPExceptionを投げる"""
    LOGGER.error(f"{message}: {exception}")
    if isinstance(exception, HTTPException):
        raise exception
    raise HTTPException(
        status_code=500,
        detail={
            "エラー": message,
            "詳細": str(exception),
            "提案": "詳細はログを確認してください。",
        },
    ) from exception
