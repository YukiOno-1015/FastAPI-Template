import logging
import socket
from typing import Callable

import requests
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app_state import environment_info_static
from commons.environment_master_key import EnvironmentMasterKey

# ロガー設定
LOGGER = logging.getLogger("uvicorn.access")


class ReverseProxyCheckMiddleware(BaseHTTPMiddleware):
    """
    CloudflareやX-Forwarded-Forヘッダーを解析し、リバースプロキシ自体の信頼性を検証するミドルウェア。
    """

    def __init__(self, app, trusted_proxies: list[str] | None = None) -> None:
        """
        ミドルウェアの初期化。

        Args:
            app (FastAPI): FastAPIアプリケーションインスタンス。
            trusted_proxies (list[str] | None): 信頼できるプロキシIPアドレスリスト。
        """
        LOGGER.info("ReverseProxyCheckMiddleware 初期化")
        super().__init__(app)
        self.trusted_proxies = trusted_proxies or self._build_trusted_proxies()
        LOGGER.info(f"信頼できるプロキシリスト: {self.trusted_proxies}")

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        """
        X-Forwarded-For や Cloudflare 固有のヘッダーを解析して信頼性を検証。

        Args:
            request (Request): HTTPリクエストオブジェクト。
            call_next (Callable): 次のミドルウェアまたはエンドポイントへのコールバック。

        Returns:
            Response: HTTPレスポンス。
        """
        LOGGER.info("ReverseProxyCheckMiddleware dispatch開始")

        # Cloudflare 固有のヘッダーを取得
        cf_connecting_ip = request.headers.get("cf-connecting-ip")
        true_client_ip = request.headers.get("true-client-ip")
        x_forwarded_for = request.headers.get("x-forwarded-for")

        LOGGER.debug(f"CF-Connecting-IP: {cf_connecting_ip}")
        LOGGER.debug(f"True-Client-IP: {true_client_ip}")
        LOGGER.debug(f"X-Forwarded-For: {x_forwarded_for}")

        # リバースプロキシIPを取得
        reverse_proxy_ip = request.client.host
        LOGGER.debug(f"リバースプロキシIP: {reverse_proxy_ip}")

        # リバースプロキシIPが信頼できるかを確認
        if not self._is_trusted_ip(reverse_proxy_ip):
            LOGGER.warning(f"信頼されていないリバースプロキシIPが検出されました: {reverse_proxy_ip}")
            return Response(content="Unauthorized Proxy", status_code=403)

        LOGGER.info(f"リバースプロキシIP {reverse_proxy_ip} は信頼リストに含まれています。")

        # リクエストを処理
        return await call_next(request)

    def _build_trusted_proxies(self) -> list[str]:
        """
        信頼できるプロキシのIPアドレスリストを動的に構築。

        Returns:
            list[str]: 信頼できるプロキシIPアドレスリスト。
        """
        trusted_proxies: list[str] = []

        # CloudflareのIPアドレスを取得
        default_ipv4_url = "https://www.cloudflare.com/ips-v4"
        default_ipv6_url = "https://www.cloudflare.com/ips-v6"

        cloudflare_ipv4_url: str = _get_environment_value(
            EnvironmentMasterKey.CLOUD_FLARE_IP_LIST_IPV4.value, default=default_ipv4_url
        )
        cloudflare_ipv6_url: str = _get_environment_value(
            EnvironmentMasterKey.CLOUD_FLARE_IP_LIST_IPV6.value, default=default_ipv6_url
        )

        try:
            ipv4_response = requests.get(cloudflare_ipv4_url)
            ipv6_response = requests.get(cloudflare_ipv6_url)
            ipv4_response.raise_for_status()
            ipv6_response.raise_for_status()

            trusted_proxies.extend(ipv4_response.text.splitlines())
            trusted_proxies.extend(ipv6_response.text.splitlines())
            LOGGER.info("Cloudflare IPアドレスを取得しました。")
        except requests.RequestException as e:
            LOGGER.warning(f"Cloudflare IPアドレスの取得に失敗しました: {e}")

        # ローカル環境でのプロキシIPアドレスを追加
        local_ips: list[str] = self._get_local_ip_addresses()
        trusted_proxies.extend(local_ips)

        return trusted_proxies

    def _get_local_ip_addresses(self) -> list[str]:
        """
        DockerやホストのローカルIPアドレスを動的に取得。

        Returns:
            list[str]: ローカルIPアドレスリスト。
        """
        local_ips: list[str] = ["127.0.0.1"]
        local_network_ips: list[str] = ["192.168.1.100", "172.19.0.4", "192.168.1.104"]

        try:
            hostname: str = socket.gethostname()
            host_ip: str = socket.gethostbyname(hostname)
            local_ips.append(host_ip)
            LOGGER.info(f"ホストのIPアドレスを取得しました: {host_ip}")
        except socket.error as e:
            LOGGER.warning(f"ホストIPアドレスの取得に失敗しました: {e}")

        return local_ips + local_network_ips

    def _is_trusted_ip(self, ip: str) -> bool:
        """
        指定されたIPアドレスが信頼できるプロキシリストに含まれているか確認。

        Args:
            ip (str): チェックするIPアドレス。

        Returns:
            bool: 信頼できる場合はTrue、そうでない場合はFalse。
        """
        return ip in self.trusted_proxies


def _get_environment_value(key_code: str, default: str = "") -> str:
    """
    環境設定からキーの値を取得します。

    Args:
        key_code (str): 環境設定のキー
        default (str): 環境設定が見つからなかった場合の初期値

    Returns:
        str: 環境設定の値、または初期値
    """
    value: dict[str, str] | None = environment_info_static.get(key_code)
    if not value:
        if default:
            LOGGER.warning(f"環境設定のキー '{key_code}' が見つからなかったため、初期値 '{default}' を使用します。")
            return default
        _handle_exception("環境設定の値が見つかりません", KeyError(f"Key '{key_code}' not found in environment info."))
    return value["values"]


def _handle_exception(message: str, exception: Exception) -> None:
    """
    エラーハンドリングを統一化します。

    Args:
        message (str): ログに出力するメッセージ
        exception (Exception): 発生した例外

    Raises:
        HTTPException: 例外をラップして再スロー
    """
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
