from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, HTTPException
from utils.util import create_signature
from app_state import environment_info_static
import time
import logging

# uvicornのロガーを取得
LOGGER = logging.getLogger("uvicorn")
# 定数でキーコードを管理
PROJECT_ID_KEY = "10000001"
VERSION_KEY = "10000002"
SECRET_KEY = "10000003"


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    """
    全てのレスポンスにカスタムヘッダーを追加するミドルウェア。
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # リクエストを処理
        response: Response = await call_next(request)
        # タイムスタンプを生成
        timestamp = int(time.time())

        # 環境情報を取得
        try:
            project_data = self.get_environment_info_static(PROJECT_ID_KEY)
            version_data = self.get_environment_info_static(VERSION_KEY)
            secret_data = self.get_environment_info_static(SECRET_KEY)

            project_id = project_data["values"]
            version = version_data["values"]
            secret_key = secret_data["values"]
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=f"環境情報取得エラー: {e.detail}")

        # X-Signatureを生成
        signature = create_signature(secret_key, project_id, version, timestamp)

        # ヘッダーに署名とタイムスタンプを追加
        response.headers["X-Signature"] = signature
        response.headers["X-Timestamp"] = str(timestamp)  # 現在のUNIXエポックタイムを追加

        # その他のカスタムヘッダーを追加
        response.headers["X-Source"] = "YourProjectName"
        response.headers["X-Project-ID"] = project_id
        response.headers["X-Version"] = version

        return response

    def get_environment_info_static(self, key_code: str) -> dict:
        """
        静的なenvironment_infoから指定したキーの値を取得する。

        Args:
            key_code (str): 取得するキーコード。

        Returns:
            dict: 対応する環境情報の辞書。

        Raises:
            HTTPException: キーコードに対応する値が見つからない場合。
        """
        value = environment_info_static.get(key_code)
        if not value:
            raise HTTPException(
                status_code=404,
                detail=f"Environment info not found for key_code: {key_code}",
            )
        return value
