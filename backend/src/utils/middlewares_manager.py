import os
import logging
import importlib
from starlette.middleware.base import BaseHTTPMiddleware
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi_profiler import PyInstrumentProfilerMiddleware

# uvicornのロガーを取得
LOGGER = logging.getLogger("uvicorn")


def include_all_middlewares(app):
    """
    'middlewares'ディレクトリ内のすべてのミドルウェアをアプリケーションにインクルードします。

    Args:
        app: FastAPIアプリケーションインスタンス。

    Raises:
        ValueError: appがNoneの場合に発生。
    """
    if app is None:
        raise ValueError("app引数はNoneであってはなりません。")

    middlewares_dir = os.path.join(os.path.dirname(__file__), "..", "middlewares")
    app.add_middleware(CorrelationIdMiddleware)
    # app.add_middleware(
    #     PyInstrumentProfilerMiddleware,
    #     server_app=app,
    #     profiler_output_type="html",
    #     html_file_name="/var/log/backend/profile.html",
    # )

    app.add_middleware(PyInstrumentProfilerMiddleware)

    # スキップするミドルウェアのリスト
    skip_middlewares = ["PyInstrumentProfilerMiddleware", "CorrelationIdMiddleware", "BaseHTTPMiddleware", "CORSConfig"]

    for filename in os.listdir(middlewares_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"middlewares.{filename[:-3]}"  # '.py'を除いたモジュール名
            try:
                module = importlib.import_module(module_name)
                for name in dir(module):
                    cls = getattr(module, name)
                    if isinstance(cls, type) and issubclass(cls, BaseHTTPMiddleware):
                        if cls.__name__ in skip_middlewares:
                            # スキップするミドルウェアをチェック
                            continue
                        app.add_middleware(cls)  # ミドルウェアを追加
                        LOGGER.info(f"ミドルウェア {cls.__name__} を正常にインクルードしました。")
            except Exception as e:
                LOGGER.error(f"モジュール {module_name} のインポート中にエラーが発生しました: {e}")
