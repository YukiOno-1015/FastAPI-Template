#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from typing import Any, Dict

import firebase_admin
from fastapi import HTTPException, Security, WebSocket, WebSocketDisconnect
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

    sa_path = "./utils/firebase_service_account.json"
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
    HTTP(Bearer)トークンを検証し、Firebase ユーザー情報を返却します。

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


async def verify_firebase_token_ws(ws: WebSocket, token_param: str = "token") -> Dict[str, Any]:
    """
    WebSocket 接続用のトークン検証。
    - クエリパラメータ(token)または Sec-WebSocket-Protocol からトークンを取得し検証します。

    Args:
        ws (WebSocket): WS コネクションオブジェクト
        token_param (str): トークン取得用のキー名

    Returns:
        Dict[str, Any]: Firebase 認証済みユーザーデータ

    Raises:
        WebSocketDisconnect: トークンが存在しないか検証失敗時に切断します
    """
    # SDK 初期化
    try:
        _initialize_firebase_app()
    except Exception as e:
        LOGGER.error(f"WebSocket SDK init error: {e}", exc_info=True)
        await ws.close(code=1011)
        raise WebSocketDisconnect(code=1011)

    # クエリパラメータからトークン取得
    token = ws.query_params.get(token_param)
    # Sec-WebSocket-Protocol ヘッダから取得
    if not token:
        subprotocols = ws.scope.get("subprotocols") or []
        if len(subprotocols) >= 2 and subprotocols[0] == token_param:
            token = subprotocols[1]

    # トークン未提供時
    if not token:
        LOGGER.warning("WebSocket: token is missing.")
        await ws.close(code=4401)
        raise WebSocketDisconnect(code=4401)

    # トークン検証
    try:
        decoded = auth.verify_id_token(token)
        LOGGER.debug(f"WebSocket token verified for uid={decoded.get('uid')}")
        return decoded
    except firebase_exceptions.InvalidIdTokenError:
        LOGGER.warning("WebSocket: Invalid ID token.")
        await ws.close(code=4401)
        raise WebSocketDisconnect(code=4401)
    except firebase_exceptions.ExpiredIdTokenError:
        LOGGER.warning("WebSocket: Expired ID token.")
        await ws.close(code=4401)
        raise WebSocketDisconnect(code=4401)
    except Exception as e:
        LOGGER.error(f"WebSocket: Error verifying token: {e}", exc_info=True)
        await ws.close(code=1011)
        raise WebSocketDisconnect(code=1011)
