import os
import importlib
import logging

# ロガーを設定
LOGGER = logging.getLogger("uvicorn")


def include_all_routers(app):
    """
    'routers'ディレクトリ内のすべてのルータをアプリケーションにインクルードします。
    一度インクルードされたルーターは再度インクルードしません。

    Args:
        app: FastAPIアプリケーションインスタンス。
    """
    # すでにインクルードされたルーターを追跡するセット
    included_routers = set()

    # 'routers'ディレクトリのパスを取得
    routers_dir = os.path.join(os.path.dirname(__file__), "..", "routers")

    # 'routers'ディレクトリ内の各ファイルをループで処理
    for filename in os.listdir(routers_dir):
        # Pythonファイルであることを確認し、'__init__.py'は除外
        if filename.endswith(".py") and filename != "__init__.py":
            # モジュール名を生成し、ファイルを動的にインポート
            module_name = f"routers.{filename[:-3]}"  # '.py'を除いたモジュール名
            if module_name in included_routers:
                LOGGER.warning(f"モジュール {module_name} はすでにインクルードされています。")
                continue  # すでにインクルードされている場合はスキップ

            try:
                module = importlib.import_module(module_name)

                # モジュールに'router'属性があれば、それをアプリにインクルード
                if hasattr(module, "router"):
                    app.include_router(module.router)
                    included_routers.add(module_name)  # インクルードしたモジュールを追加
                    LOGGER.info(f"ルーター {module_name} を正常にインクルードしました。")
                else:
                    LOGGER.warning(f"モジュール {module_name} に 'router' 属性がありません。")
            except Exception as e:
                LOGGER.error(f"モジュール {module_name} のインポート中にエラーが発生しました: {e}")
