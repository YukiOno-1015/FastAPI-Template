import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# uvicornのロガーを取得
LOGGER = logging.getLogger("uvicorn")


class CORSConfig:
    """
    CORS設定を管理するクラス。

    Attributes:
        app (FastAPI): FastAPIアプリケーションインスタンス。
        allow_origins (list[str]): 許可するオリジンのリスト。デフォルトはすべてのオリジンを許可する。
        allow_credentials (bool): クッキーや認証情報の送信を許可するかどうか。デフォルトはTrue。
        allow_methods (list[str]): 許可するHTTPメソッドのリスト。デフォルトはすべてのメソッドを許可する。
        allow_headers (list[str]): 許可するヘッダーのリスト。デフォルトはすべてのヘッダーを許可する。
    """

    def __init__(
        self,
        app: FastAPI,
        allow_origins: list[str] = None,
        allow_credentials: bool = True,
        allow_methods: list[str] = None,
        allow_headers: list[str] = None,
    ):
        """
        CORS設定を初期化する。

        Args:
            app (FastAPI): FastAPIアプリケーションインスタンス。
            allow_origins (list[str]): 許可するオリジンのリスト。
            allow_credentials (bool): クッキーや認証情報の送信を許可するかどうか。
            allow_methods (list[str]): 許可するHTTPメソッドのリスト。
            allow_headers (list[str]): 許可するヘッダーのリスト。
        """
        # デフォルト値の設定
        allow_origins = allow_origins or ["*"]  # デフォルト: 全オリジン許可
        allow_methods = allow_methods or ["*"]  # デフォルト: 全メソッド許可
        allow_headers = allow_headers or ["*"]  # デフォルト: 全ヘッダー許可

        # 設定の確認ログ
        LOGGER.info(
            f"CORSConfig initialized with: allow_origins={allow_origins}, "
            f"allow_credentials={allow_credentials}, allow_methods={allow_methods}, "
            f"allow_headers={allow_headers}"
        )

        # CORS ミドルウェアをアプリケーションに追加
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_credentials=allow_credentials,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
        )
