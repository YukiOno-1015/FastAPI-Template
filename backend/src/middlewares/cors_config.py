# cors_config.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


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
        if allow_origins is None:
            allow_origins = ["*"]  # デフォルト値: すべてのオリジンを許可
        if allow_methods is None:
            allow_methods = ["*"]  # デフォルト値: すべてのメソッドを許可
        if allow_headers is None:
            allow_headers = ["*"]  # デフォルト値: すべてのヘッダーを許可

        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_credentials=allow_credentials,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
        )
