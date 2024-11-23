import importlib
import logging
import os

from fastapi import FastAPI

# ロガーを設定
LOGGER = logging.getLogger("uvicorn")

# 除外するファイルのリスト
EXCLUDED_FILES = ["__init__.py", "protocol.py"]


def include_all_routers(app: FastAPI, routers_dir: str = "routers"):
    """
    指定されたディレクトリ内のすべてのルーターをFastAPIアプリケーションにインクルードします。
    一度インクルードされたルーターは再度インクルードしません。

    Args:
        app (FastAPI): FastAPIアプリケーションインスタンス。
        routers_dir (str): ルーターが含まれるディレクトリ名（デフォルト: "routers"）。

    Raises:
        FileNotFoundError: 指定されたディレクトリが存在しない場合。
    """
    # インクルード済みのルーターを追跡するセット
    included_routers = set()

    # ルーターのディレクトリパスを取得
    base_dir = os.path.dirname(os.path.abspath(__file__))
    routers_path = os.path.join(base_dir, "..", routers_dir)

    # ディレクトリが存在しない場合は例外をスロー
    if not os.path.isdir(routers_path):
        raise FileNotFoundError(f"指定されたルーターのディレクトリが存在しません: {routers_path}")

    # ルーターのファイルを探索
    for filename in os.listdir(routers_path):
        # 除外リストに含まれないPythonファイルを対象とする
        if filename.endswith(".py") and filename not in EXCLUDED_FILES:
            module_name = f"{routers_dir}.{filename[:-3]}"  # '.py' を除いたモジュール名

            # モジュールがすでにインクルードされている場合はスキップ
            if module_name in included_routers:
                LOGGER.warning(f"モジュール {module_name} はすでにインクルードされています。")
                continue

            try:
                # モジュールを動的にインポート
                module = importlib.import_module(module_name)

                # 'router' 属性が存在する場合はアプリにインクルード
                if hasattr(module, "router"):
                    app.include_router(module.router)
                    included_routers.add(module_name)  # インクルード済みに追加
                    LOGGER.info(f"ルーター {module_name} を正常にインクルードしました。")
                else:
                    LOGGER.warning(f"モジュール {module_name} に 'router' 属性がありません。スキップします。")
            except Exception as e:
                LOGGER.error(f"モジュール {module_name} のインポート中にエラーが発生しました: {e}")
