# settings.py
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # アプリ基本情報
    title: str = "FastAPI Template Updated"
    version: str = "0.0.1"
    description: str = "FastAPI Template"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    redirect_slashes: bool = False

    # CORS 設定
    # カンマ区切りで受け取る（デフォルトは "*"）
    cors_allow_origins: Optional[str] = "*"
    cors_allow_methods: Optional[str] = "*"
    cors_allow_headers: Optional[str] = "*"
    cors_allow_credentials: bool = True

    class Config:
        env_file = ".env"


# グローバルに使える設定インスタンス
settings = Settings()
