import os
import time
from requests.exceptions import HTTPError
from utils.my_logger import setup_logger
from collections.abc import Callable

# スクリプトのパスを取得してロガーを設定
script_path: str = os.path.realpath(__file__)
LOGGER = setup_logger(script_path)


def check_value(value: str | None) -> str:
    """
    値がNoneまたは空文字の場合にエラーを発生させます。

    Args:
        value (str | None): チェックする文字列。Noneまたは空文字の場合はエラーが発生します。

    Returns:
        str: 有効な文字列が返されます。

    Raises:
        ValueError: 値がNoneまたは空文字の場合に発生します。
    """
    if value is None or value == "":
        raise ValueError("値がNoneまたは空文字です")
    return value


# 再試行用の関数
def retry_request(
    func: Callable[[], any],  # type: ignore
    max_retries: int = 10,
    initial_wait_time: int = 5,
    backoff_factor: int = 2,
) -> any:  # type: ignore
    """
    APIリクエストを再試行する関数

    Args:
        func (Callable[[], any]): 呼び出す関数。
        max_retries (int): 最大再試行回数。デフォルトは10回。
        initial_wait_time (int): 初回待機時間（秒単位）。デフォルトは5秒。
        backoff_factor (int): バックオフファクター（待機時間の増加率）。デフォルトは2倍。

    Returns:
        any: 呼び出された関数の戻り値。

    Raises:
        Exception: 最大再試行回数に達した場合に発生します。
    """
    wait_time: int = initial_wait_time
    for attempt in range(max_retries):
        try:
            return func()  # 関数を実行
        except HTTPError as e:
            # ステータスコードが503の場合、再試行
            status_code = e.response.status_code if hasattr(e, "response") else None
            if status_code == 503:
                LOGGER.error(
                    f"APIリクエストエラー: {e}, ステータスコード: {status_code}, 再試行回数: {attempt + 1}/{max_retries}, 待機時間: {wait_time} 秒"
                )
                time.sleep(wait_time)  # 待機
                wait_time *= backoff_factor  # 再試行ごとに待機時間を指数関数的に増加
            else:
                LOGGER.error(f"APIリクエストエラー: {e}")
                break
        except Exception as e:
            LOGGER.error(f"リクエストエラー: {e}")
            break
    raise Exception(f"最大再試行回数に達しました: {max_retries}")
