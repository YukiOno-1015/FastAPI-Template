import time
import logging
import hmac
import hashlib
import base64
from requests.exceptions import HTTPError
from fastapi import HTTPException
from collections.abc import Callable
from services.environment_service import EnvironmentService


# uvicornのロガーを取得
LOGGER = logging.getLogger("uvicorn")


def check_value(value: str | None) -> str:
    """
    値がNoneまたは空文字の場合に404エラーを発生させます。

    Args:
        value (str | None): チェックする文字列。Noneまたは空文字の場合は404エラーが発生します。

    Returns:
        str: 有効な文字列が返されます。

    Raises:
        HTTPException: 値がNoneまたは空文字の場合に404エラーが発生します。
    """
    if value is None or value == "":
        raise HTTPException(
            status_code=404, detail="提供された値はNoneまたは空文字です。"
        )
    return value


def retry_request(
    func: Callable[[], any],  # type: ignore
    max_retries: int = 10,
    initial_wait_time: int = 5,
    backoff_factor: int = 2,
) -> any:  # type: ignore
    """
    APIリクエストを再試行する関数。

    Args:
        func (Callable[[], any]): 呼び出す関数。
        max_retries (int): 最大再試行回数。デフォルトは10回。
        initial_wait_time (int): 初回待機時間（秒単位）。デフォルトは5秒。
        backoff_factor (int): 待機時間の増加率。デフォルトは2倍。

    Returns:
        any: 呼び出された関数の戻り値。

    Raises:
        HTTPException: 最大再試行回数に達した場合に発生します。
    """
    wait_time: int = initial_wait_time
    for attempt in range(max_retries):
        try:
            return func()  # 関数を実行
        except HTTPError as e:
            status_code = e.response.status_code if hasattr(e, "response") else None
            if status_code == 503:
                LOGGER.error(
                    f"APIリクエストエラー: {e}, ステータスコード: {status_code}, "
                    f"再試行回数: {attempt + 1}/{max_retries}, 待機時間: {wait_time} 秒"
                )
                time.sleep(wait_time)  # 待機
                wait_time *= backoff_factor  # 待機時間を指数関数的に増加
            else:
                LOGGER.error(f"APIリクエストエラー: {e}")
                raise HTTPException(status_code=status_code or 500, detail=str(e))
        except Exception as e:
            LOGGER.error(f"リクエストエラー: {e}")
            raise HTTPException(status_code=500, detail="内部エラーが発生しました")

    raise HTTPException(status_code=503, detail="最大再試行回数に達しました")


def create_signature(
    secret_key: str, project_id: str, version: str, timestamp: int
) -> str:
    """
    データのハッシュ署名を生成します。

    Args:
        secret_key (str): 署名を生成するための秘密鍵。
        project_id (str): プロジェクトの一意の識別子。
        version (str): APIまたはアプリケーションのバージョン。
        timestamp (int): タイムスタンプ。

    Returns:
        str: データのハッシュ署名（Base64エンコード）。
    """
    data_to_sign = f"{project_id}:{version}:{timestamp}"  # データを組み合わせ
    signature = hmac.new(
        key=secret_key.encode(), msg=data_to_sign.encode(), digestmod=hashlib.sha256
    )
    return base64.b64encode(signature.digest()).decode()
