import logging
import time

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app_state import environment_info_static
from commons.environment_master_key import EnvironmentMasterKey
from utils.util import create_signature, encode_to_base64

# uvicornのロガーを取得
LOGGER = logging.getLogger("uvicorn")


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    """
    全てのレスポンスにカスタムヘッダーを追加するミドルウェア。
    """

    def __init__(self, app):
        LOGGER.info("CustomHeaderMiddleware 初期化")
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        LOGGER.info("CustomHeaderMiddleware dispatch開始")
        # タイムスタンプを生成
        timestamp = int(time.time())

        # 環境情報を取得
        try:
            project_id = self.__get_environment_info_static(EnvironmentMasterKey.PROJECT_ID.value)["values"]
            version = self.__get_environment_info_static(EnvironmentMasterKey.VERSION.value)["values"]
            secret_key = self.__get_environment_info_static(EnvironmentMasterKey.SECRET.value)["values"]
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=f"環境情報取得エラー: {e.detail}")

        # リクエストを処理し、レスポンスを取得
        response: Response = await call_next(request)

        # レスポンスボディ全体を非同期に読み込む
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        # X-Signatureを生成
        signature = create_signature(secret_key, project_id, version, timestamp, body.decode("utf-8"))

        # カスタムヘッダーを追加
        response.headers["X-Signature"] = signature
        response.headers["X-Timestamp"] = str(timestamp)
        response.headers["X-Project-ID"] = encode_to_base64(project_id)
        response.headers["X-Version"] = encode_to_base64(version)

        # レスポンスボディを再設定
        async def new_body_iterator():
            yield body

        response.body_iterator = new_body_iterator()

        return response

    def __get_environment_info_static(self, key_code: str) -> dict:
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
