import os


def find_top_level_modules(project_dir):
    """
    プロジェクトディレクトリ内のトップレベルモジュールを検出する関数。

    Args:
        project_dir (str): プロジェクトのルートディレクトリのパス。

    Returns:
        list[str]: 検出されたトップレベルモジュール名のリスト。
    """
    modules = []
    for item in os.listdir(project_dir):
        item_path = os.path.join(project_dir, item)
        # ディレクトリであり、__init__.py が存在する場合
        if os.path.isdir(item_path) and os.path.isfile(os.path.join(item_path, "__init__.py")):
            modules.append(item)
    return modules


if __name__ == "__main__":
    # 実行時にプロジェクトのルートパスを指定
    project_root = "./"  # 必要に応じてプロジェクトのパスを指定
    modules = find_top_level_modules(project_root)
    print("Detected top-level modules:", modules)
