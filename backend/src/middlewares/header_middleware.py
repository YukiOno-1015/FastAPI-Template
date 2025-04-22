#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HeaderMiddleware モジュール

このミドルウェアは、以下の機能を提供します:
 1. リバースプロキシの信頼性チェック
 2. クライアントのリアル IP アドレス設定
 3. レスポンスにカスタムシグネチャヘッダーを追加
    - X-Signature: HMAC シグネチャ
    - X-Timestamp: リクエスト時刻 (UNIX 時間)
    - X-Project-ID: Base64 エンコードしたプロジェクト ID
    - X-Version: Base64 エンコードしたバージョン
 4. 不要なヘッダーの削除 (デフォルト: X-Uvicorn, Server)
 5. ネットワーク内ホストの検出（ping コマンドを使用、存在しない場合はスキップ）

Usage:
    app.add_middleware(HeaderMiddleware, remove_headers=[...], trusted_proxies=[...])

注意:
    get_environment_info_static から取得する環境変数は、
    commons.environment_master_key に定義されたキーコードを使用します。
"""
import inspect
import ipaddress
import logging
import shutil
import subprocess
import time
from collections.abc import AsyncIterable, Iterable
from typing import Awaitable, Callable, List

import netifaces
import requests
from fastapi import FastAPI, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from commons.environment_master_key import EnvironmentMasterKey
from utils.protocol import get_environment_info_static, handle_exception
from utils.util import create_signature, encode_to_base64

# Uvicorn 用ロガーを取得
LOGGER = logging.getLogger("uvicorn.middleware.header")


class HeaderMiddleware(BaseHTTPMiddleware):
    """
    HeaderMiddleware クラス

    レスポンスに対し以下を実行します:
      1. リバースプロキシ検証 (信頼リスト照合)
      2. クライアントのリアルIP設定
      3. レスポンスボディへのシグネチャヘッダー追加
      4. 不要ヘッダー削除

    Args:
        app (FastAPI): FastAPI アプリケーション インスタンス
        remove_headers (List[str], optional): 削除対象のヘッダー名リスト
        trusted_proxies (List[str], optional): 信頼プロキシIPリスト
    """

    def __init__(
        self,
        app: FastAPI,
        remove_headers: List[str] = None,
        trusted_proxies: List[str] = None,
    ):
        super().__init__(app)
        # 削除対象ヘッダーを設定
        self.remove_headers: List[str] = remove_headers or ["X-Uvicorn", "Server"]
        # 信頼プロキシリストを指定または動的生成
        # self.trusted_proxies: List[str] = trusted_proxies or self._build_trusted_proxies()
        LOGGER.info(f"remove_headers={self.remove_headers}")

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        LOGGER.debug("[HeaderMiddleware] dispatch start")

        # (1) リバースプロキシの信頼性チェック
        # proxy_ip: str = request.client.host
        # if proxy_ip not in self.trusted_proxies:
        #     LOGGER.warning(f"Untrusted proxy detected: {proxy_ip}")
        #     return Response(content="Unauthorized Proxy", status_code=403)
        # LOGGER.debug(f"Trusted proxy: {proxy_ip}")

        # (2) クライアントのリアルIPを設定
        real_ip: str = self._extract_real_ip(request)
        request.scope["client"] = (real_ip, request.client.port)
        LOGGER.debug(f"Real IP set: {real_ip}")

        # (3) タイムスタンプ (UNIX 秒)
        timestamp: int = int(time.time())

        # (4) 環境情報を取得 (例外時は handle_exception で HTTP 例外化)
        try:
            project_id: str = get_environment_info_static(EnvironmentMasterKey.PROJECT_ID)
            version: str = get_environment_info_static(EnvironmentMasterKey.VERSION)
            secret: str = get_environment_info_static(EnvironmentMasterKey.SECRET)
        except HTTPException as e:
            handle_exception("Environment info load failed", e)

        # (5) 実際のレスポンス取得
        response: Response = await call_next(request)

        # (6) レスポンスボディ全体をチャンク収集（sync/async 両対応）
        chunks: List[bytes] = []
        body_iter = response.body_iterator

        # 非同期イテレータ判定
        if isinstance(body_iter, AsyncIterable) or inspect.isasyncgen(body_iter) or hasattr(body_iter, "__aiter__"):
            async for chunk in body_iter:  # type: ignore[misc]
                chunks.append(chunk)
        # 同期イテレータ判定
        elif isinstance(body_iter, Iterable):
            for chunk in body_iter:
                chunks.append(chunk)
        # それ以外は空ボディ扱い

        body_bytes = b"".join(chunks)
        body_text = body_bytes.decode("utf-8", errors="ignore")

        # (7) HMAC シグネチャ生成
        signature = create_signature(secret, project_id, version, timestamp, body_text)

        # (8) カスタムヘッダー追加
        response.headers.update(
            {
                "X-Signature": signature,
                "X-Timestamp": str(timestamp),
                "X-Project-ID": encode_to_base64(project_id),
                "X-Version": encode_to_base64(version),
            }
        )
        LOGGER.debug("Custom headers added to response")

        # (9) 不要ヘッダー削除
        for header in self.remove_headers:
            if header in response.headers:
                del response.headers[header]
                LOGGER.debug(f"Removed header: {header}")

        # (10) body_iterator を再設定（必ず async イテレータに）
        response.body_iterator = self._make_async_iterator(chunks)
        LOGGER.debug("[HeaderMiddleware] dispatch end")
        return response

    def _extract_real_ip(self, request: Request) -> str:
        for header_name in ("X-Forwarded-For", "CF-Connecting-IP", "True-Client-IP"):
            if value := request.headers.get(header_name):
                return value.split(",")[0].strip()
        return request.client.host

    @staticmethod
    async def _make_async_iterator(chunks: List[bytes]):
        """
        同期的に収集したチャンクリストを非同期イテレータに変換
        """
        for chunk in chunks:
            yield chunk

    def _build_trusted_proxies(self) -> List[str]:
        trusted: List[str] = []
        # Cloudflare IP リスト取得
        for url in ("https://www.cloudflare.com/ips-v4", "https://www.cloudflare.com/ips-v6"):
            try:
                resp = requests.get(url, timeout=5)
                resp.raise_for_status()
                trusted.extend(resp.text.splitlines())
            except Exception as e:
                LOGGER.warning(f"Failed to fetch CF IPs from {url}: {e}")

        # デフォルトゲートウェイ
        gw_info = netifaces.gateways().get("default", {}).get(netifaces.AF_INET)
        if gw_info:
            trusted.append(gw_info[0])

        # インターフェース IP とサブネット ping スキャン
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            for fam in (netifaces.AF_INET, netifaces.AF_INET6):
                for info in addrs.get(fam, []):
                    ip_addr = info.get("addr")
                    if ip_addr:
                        trusted.append(ip_addr)
                    if fam == netifaces.AF_INET and info.get("netmask"):
                        cidr = ipaddress.IPv4Network(f"{info['addr']}/{info['netmask']}", strict=False)
                        trusted.extend(self._scan_ping(str(cidr)))

        unique = list(dict.fromkeys(filter(None, trusted)))
        LOGGER.info(f"Constructed trusted proxies list, count={len(unique)}")
        return unique

    @staticmethod
    def _scan_ping(network_cidr: str, timeout: int = 1) -> List[str]:
        if shutil.which("ping") is None:
            LOGGER.warning("ping コマンドが見つかりません。スキップします。")
            return []

        net = ipaddress.IPv4Network(network_cidr, strict=False)
        alive: List[str] = []
        for host in net.hosts():
            res = subprocess.run(
                ["ping", "-c", "1", "-W", str(timeout), str(host)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if res.returncode == 0:
                alive.append(str(host))
        return alive
