#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
共通プロトコルユーティリティ
- APIRouter 作成
- Bearer トークン抽出
- 静的キャッシュから環境情報取得
- 例外ハンドリング
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException  # noqa: F401
from fastapi.security import APIKeyHeader
from fastapi_versioning import version  # noqa: F401
from sqlalchemy.orm import Session  # noqa: F401

from app_state import environment_info_static
from commons.environment_master_key import EnvironmentMasterKey

# Uvicorn 用ロガー取得
LOGGER = logging.getLogger("uvicorn.protocol")

# Bearer トークン抽出用セキュリティスキーマ
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def extract_token(authorization: str) -> str:
    """
    Authorization ヘッダーから Bearer トークンを抽出します。
    """
    if not authorization:
        LOGGER.error("Authorization header missing.")
        raise HTTPException(status_code=401, detail="Authorization header missing.")
    token = authorization.replace("Bearer ", "")
    LOGGER.debug(f"[Protocol] Token extracted: {token}")
    return token


def create_router(prefix: str, tags: List[str]) -> APIRouter:
    """
    APIRouter を生成し、共通プレフィックスとタグを設定します。
    """
    router = APIRouter(prefix=prefix, tags=tags)
    LOGGER.debug(f"[Protocol] Router created: prefix={prefix}, tags={tags}")
    return router


def get_environment_info_static(key_code: EnvironmentMasterKey) -> str:
    """
    静的キャッシュから指定キーの環境情報を取得します。
    """

    entry: Optional[Dict[str, Any]] = environment_info_static.get(key_code.value)
    if entry is None:
        handle_exception(
            message=f"環境情報が見つかりません: {key_code.value}",
            exception=KeyError(f"{key_code.value} not found in cache"),
        )
    value = entry.get("values")
    if value is None:
        handle_exception(
            message=f"環境情報の値が空です: {key_code.value}", exception=ValueError(f"No values for {key_code.value}")
        )
    return value


def get_environment_value(key_code: str) -> str:
    """
    静的キャッシュから文字列キーの環境情報を取得します。
    """
    from app_state import environment_info_static  # 遅延インポート

    entry: Optional[Dict[str, Any]] = environment_info_static.get(key_code)
    if entry is None:
        handle_exception(
            message=f"環境設定 '{key_code}' が存在しません", exception=KeyError(f"{key_code} not found in cache")
        )
    value = entry.get("values")
    if value is None:
        handle_exception(message=f"環境設定 '{key_code}' の値が空です", exception=ValueError("No value"))
    return value


def handle_exception(message: str, exception: Exception) -> None:
    """
    共通例外ハンドラ: ログ出力のうえ HTTPException に変換して送出します。
    """
    LOGGER.error(f"{message}: {exception}", exc_info=True)
    if isinstance(exception, HTTPException):
        raise exception
    raise HTTPException(
        status_code=500,
        detail={
            "error": message,
            "details": str(exception),
            "hint": "サーバログを確認してください。",
        },
    ) from exception
