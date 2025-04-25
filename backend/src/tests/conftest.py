"""
conftest.py

pytest 設定および FastAPI テスト環境初期化
"""

import datetime
import os
import sys

import pytest
from fastapi.testclient import TestClient

# ───────────────────────────────────────────────────────────────────────────
# プロジェクトルート (backend/src) をモジュール検索パスに追加
# ───────────────────────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app_state import environment_info_static

# main.py と environment_info_static をインポート
from main import create_app

# ───────────────────────────────────────────────────────────────────────────
# テスト用環境情報データ定義
# INSERT INTO environment_info ... を元にしています
# ───────────────────────────────────────────────────────────────────────────
TEST_ENV_INFOS = [
    {
        "key_code": "10000001",
        "values": "MemoCho",
        "created_by": "YukiOno",
        "updated_by": "YukiOno",
        "created_at": datetime.datetime(2025, 4, 20, 0, 0, 0),
        "updated_at": datetime.datetime(2025, 4, 20, 0, 0, 0),
    },
    {
        "key_code": "10000002",
        "values": "0.0.1",
        "created_by": "YukiOno",
        "updated_by": "YukiOno",
        "created_at": datetime.datetime(2025, 4, 20, 0, 0, 0),
        "updated_at": datetime.datetime(2025, 4, 20, 0, 0, 0),
    },
    {
        "key_code": "10000003",
        "values": "c8e8a31e7ec5500f5228e2ed3c36bb7b42d7376c5f54d46273d63e4bfef59dbe",
        "created_by": "YukiOno",
        "updated_by": "YukiOno",
        "created_at": datetime.datetime(2025, 4, 20, 0, 0, 0),
        "updated_at": datetime.datetime(2025, 4, 20, 0, 0, 0),
    },
]


@pytest.fixture(autouse=True)
def setup_environment_info():
    """
    各テスト前に environment_info_static を初期化し、
    TEST_ENV_INFOS の内容をセットします。
    """
    # 既存データクリア
    environment_info_static.clear()
    # テストデータ挿入
    for info in TEST_ENV_INFOS:
        environment_info_static[info["key_code"]] = {
            "key_code": info["key_code"],
            "values": info["values"],
            "created_by": info["created_by"],
            "updated_by": info["updated_by"],
            "created_at": info["created_at"],
            "updated_at": info["updated_at"],
        }


@pytest.fixture(scope="session")
def app():
    """FastAPI アプリ本体を生成"""
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    """TestClient を提供"""
    return TestClient(app)
