#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
プロジェクトディレクトリ内のトップレベルモジュールを検出するスクリプト。

Usage:
    python find_modules.py /path/to/project_root
"""

import sys
from pathlib import Path
from typing import List


def find_top_level_modules(project_dir: Path) -> List[str]:
    """
    プロジェクトディレクトリ内のトップレベルモジュールを検出します。

    * ディレクトリでかつ __init__.py を含むものを「パッケージ」とみなします。
    * .git や __pycache__ は自動的にスキップします。

    Args:
        project_dir (Path): プロジェクトのルートディレクトリの Path オブジェクト。

    Returns:
        List[str]: 検出されたトップレベルモジュール名のリスト。
    """
    modules: List[str] = []
    for child in project_dir.iterdir():
        # パッケージとみなす条件：ディレクトリかつ __init__.py が存在
        if not child.is_dir():
            continue
        if child.name.startswith((".", "__", "tests", "venv")):
            # 隠しディレクトリやテスト・仮想環境はスキップ
            continue
        if (child / "__init__.py").is_file():
            modules.append(child.name)
    return modules


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_modules.py <project_root>")
        sys.exit(1)

    project_root = Path(sys.argv[1]).resolve()
    if not project_root.is_dir():
        print(f"Error: {project_root} is not a directory.")
        sys.exit(1)

    modules = find_top_level_modules(project_root)
    if modules:
        print("Detected top-level modules:")
        for name in modules:
            print(f"  - {name}")
    else:
        print("No top-level modules found.")


if __name__ == "__main__":
    main()
