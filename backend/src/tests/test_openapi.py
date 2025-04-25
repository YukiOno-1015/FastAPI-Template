"""
test_openapi.py

OpenAPI ドキュメント取得テスト

このモジュールでは、バージョニングされた FastAPI アプリケーションに対して
/v0_1 および /latest プレフィックスを用いた OpenAPI スキーマの取得と
必須フィールドの検証を行います。
"""

import pytest
from fastapi.testclient import TestClient


def test_openapi_json_endpoints_exist(client: TestClient):
    """
    /v0_1/openapi.json および /latest/openapi.json エンドポイントが
    正常に応答し、HTTP 200 を返すことを検証します。
    """
    # テスト対象のエンドポイントプレフィックス一覧
    prefixes = ("/v0_1", "/latest")
    for prefix in prefixes:
        url = f"{prefix}/openapi.json"
        # エンドポイントへ GET リクエスト
        response = client.get(url)
        # ステータスコードが 200 であることを確認
        assert response.status_code == 200, f"Expected status code 200 for {url}, got {response.status_code}"


def test_openapi_json_schema_fields(client: TestClient):
    """
    取得した OpenAPI スキーマ JSON に、必須のキー 'openapi' および 'paths' が
    含まれていることを検証します。
    """
    prefixes = ("/v0_1", "/latest")
    for prefix in prefixes:
        url = f"{prefix}/openapi.json"
        # JSON レスポンスをパース
        response = client.get(url)
        data = response.json()
        # 'openapi' キーの存在確認
        assert "openapi" in data, f"'openapi' key not found in schema from {url}"
        # 'paths' キーの存在確認
        assert "paths" in data, f"'paths' key not found in schema from {url}"
