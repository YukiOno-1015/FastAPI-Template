import os
import importlib

def include_all_routers(app):
    # 'routers'ディレクトリのパスを取得
    routers_dir = os.path.join(os.path.dirname(__file__), '..', 'routers')

    # 'routers'ディレクトリ内の各ファイルをループで処理
    for filename in os.listdir(routers_dir):
        # Pythonファイルであることを確認し、'__init__.py'は除外
        if filename.endswith(".py") and filename != "__init__.py":
            # モジュール名を生成し、ファイルを動的にインポート
            module_name = f"routers.{filename[:-3]}"  # '.py'を除いたモジュール名
            module = importlib.import_module(module_name)

            # モジュールに'router'属性があれば、それをアプリにインクルード
            if hasattr(module, "router"):
                # ルーターにtagsなどの設定がある場合はそのままインクルード
                app.include_router(module.router)
