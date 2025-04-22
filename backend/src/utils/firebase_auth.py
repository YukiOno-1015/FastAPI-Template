#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from typing import Any, Dict

import firebase_admin
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials
from firebase_admin import exceptions as firebase_exceptions

# Uvicorn 用ロガー取得
LOGGER = logging.getLogger("uvicorn.auth")

# セキュリティスキーマ (Bearer Token)
security = HTTPBearer()

# Firebase Admin SDK 初期化 (singleton)
FIREBASE_APP = None


def _initialize_firebase_app():
    """
    Firebase Admin SDK を初期化します。
    SERVICE_ACCOUNT_PATH 環境変数またはデフォルトパスから認証情報を読み込む。
    """
    global FIREBASE_APP
    if FIREBASE_APP is not None:
        return FIREBASE_APP

    sa_path = os.getenv("FIREBASE_SERVICE_ACCOUNT", "./utils/firebase_service_account.json")
    if not os.path.isfile(sa_path):
        LOGGER.error(f"Firebase service account file not found: {sa_path}")
        raise RuntimeError("Firebase service account file is missing.")

    try:
        cred = credentials.Certificate(sa_path)
        FIREBASE_APP = firebase_admin.initialize_app(cred)
        LOGGER.info("Firebase Admin SDK initialized successfully.")
        return FIREBASE_APP
    except Exception as e:
        LOGGER.error(f"Failed to initialize Firebase Admin SDK: {e}", exc_info=True)
        raise RuntimeError("Unable to initialize Firebase Admin SDK.") from e


async def verify_firebase_token(auth_credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """
    Bearer トークンを検証し、Firebase ユーザー情報を返却します。

    Args:
        auth_credentials (HTTPAuthorizationCredentials): Authorization ヘッダーからの認証情報

    Returns:
        Dict[str, Any]: Firebase 認証済みユーザーデータ (uid, email など)

    Raises:
        HTTPException: トークンが無効、期限切れ、または SDK 初期化失敗時
    """
    # Firebase SDK の初期化を試みる
    try:
        _initialize_firebase_app()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    token = auth_credentials.credentials
    if not token:
        LOGGER.warning("Authorization header missing or empty.")
        raise HTTPException(status_code=401, detail="Authorization header missing or empty.")

    try:
        decoded = auth.verify_id_token(token)
        LOGGER.debug(f"Token verified for uid={decoded.get('uid')}")
        return decoded
    except firebase_exceptions.InvalidIdTokenError:
        LOGGER.warning("Invalid Firebase ID token.")
        raise HTTPException(status_code=401, detail="Invalid Firebase ID token.")
    except firebase_exceptions.ExpiredIdTokenError:
        LOGGER.warning("Expired Firebase ID token.")
        raise HTTPException(status_code=401, detail="Expired Firebase ID token.")
    except firebase_exceptions.RevokedIdTokenError:
        LOGGER.warning("Revoked Firebase ID token.")
        raise HTTPException(status_code=401, detail="Revoked Firebase ID token.")
    except Exception as e:
        LOGGER.error(f"Error verifying Firebase token: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal authentication error.")
