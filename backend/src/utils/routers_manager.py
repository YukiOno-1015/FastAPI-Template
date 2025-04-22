#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ルーター自動登録モジュール
- DDD 構成または単一 src ディレクトリ配下をスキャン
- subpkg/router.py を持つ各ディレクトリを自動で FastAPI に登録
"""
import importlib
import logging
import os
import pkgutil
from typing import Optional, Set

from fastapi import FastAPI

# Uvicorn 用ロガー取得
LOGGER = logging.getLogger("uvicorn.routers_manager")

# 除外するディレクトリ一覧
EXCLUDED_DIRS: Set[str] = {"__pycache__", "utils", "config", "core", "middlewares", "schemas", "models"}


def include_all_routers(app: FastAPI, root_dir: str = "./routers", root_pkg: Optional[str] = None) -> None:
    """
    指定ディレクトリを走査し、router.py を含むサブパッケージを FastAPI に登録します。

    Args:
        app (FastAPI): FastAPI アプリケーションインスタンス
        root_dir (str): ルーター配置ディレクトリのパス (ファイルシステム上)
        root_pkg (Optional[str]): import 時のパッケージプレフィックス (例: "app"), None ならプレフィックスなし
    """
    pkg_path = os.path.abspath(root_dir)
    if not os.path.isdir(pkg_path):
        LOGGER.error(f"ルーター検索ディレクトリが存在しません: {pkg_path}")
        return

    # ディレクトリ直下のサブディレクトリを走査
    for finder, module_name, is_pkg in pkgutil.iter_modules([pkg_path]):
        if not is_pkg or module_name in EXCLUDED_DIRS:
            continue

        module_path = os.path.join(pkg_path, module_name)
        router_file = os.path.join(module_path, "router.py")
        if not os.path.isfile(router_file):
            LOGGER.debug(f"{module_name}/router.py が存在しません。スキップ。")
            continue

        # import 名の組み立て
        if root_pkg:
            import_name = f"{root_pkg}.{module_name}.router"
        else:
            import_name = f"{module_name}.router"

        LOGGER.debug(import_name)
        try:
            mod = importlib.import_module(import_name)
        except Exception as e:
            LOGGER.error(f"{import_name} のインポートエラー: {e}", exc_info=True)
            continue

        # router 属性を持っていれば登録
        if hasattr(mod, "router"):
            app.include_router(mod.router)
            LOGGER.info(f"ルーター登録: {import_name}")
        else:
            LOGGER.warning(f"{import_name} に router 属性がありません。登録をスキップ。")
