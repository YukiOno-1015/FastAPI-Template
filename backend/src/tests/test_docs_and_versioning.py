"""
test_docs_and_versioning.py

Swagger UI と ReDoc UI 取得テスト

このモジュールでは、バージョニングされた FastAPI アプリケーションに対して以下を検証します：

1. `/v0_1/docs` および `/latest/docs` へのアクセスで Swagger UI が表示されること
2. `/v0_1/redoc` および `/latest/redoc` へのアクセスで ReDoc UI が表示されること

各 UI ページのステータスコードと、主要なスクリプトタグの存在をチェックします。
"""

import pytest
from fastapi.testclient import TestClient


def test_swagger_ui_pages(client: TestClient):
    """
    `/v0_1/docs` および `/latest/docs` エンドポイントにアクセスし、
    HTTP 200 が返却され、Swagger UI の主要なスクリプトが含まれていることを検証します。
    """
    docs_paths = ("/v0_1/docs", "/latest/docs")
    for path in docs_paths:
        response = client.get(path)
        # ステータスコードの確認
        assert response.status_code == 200, f"Expected 200 for Swagger UI at {path}, got {response.status_code}"
        # Swagger UI の主要スクリプト (SwaggerUIBundle) の存在確認
        assert "SwaggerUIBundle" in response.text, f"SwaggerUIBundle not found in response at {path}"


def test_redoc_ui_pages(client: TestClient):
    """
    `/v0_1/redoc` および `/latest/redoc` エンドポイントにアクセスし、
    HTTP 200 が返却され、ReDoc UI のスクリプトが含まれていることを検証します。
    """
    redoc_paths = ("/v0_1/redoc", "/latest/redoc")
    for path in redoc_paths:
        response = client.get(path)
        # ステータスコードの確認
        assert response.status_code == 200, f"Expected 200 for ReDoc UI at {path}, got {response.status_code}"
        # ReDoc standalone JS の存在確認
        assert "redoc.standalone.js" in response.text, f"ReDoc standalone script not found in response at {path}"
