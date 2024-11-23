from datetime import datetime

from fastapi_camelcase import CamelModel
from pydantic import Field


class EnvironmentInfoSchema(CamelModel):
    """
    EnvironmentInfoモデルのスキーマ。
    環境設定情報を管理するためのレスポンス用スキーマ。
    """

    key_code: str = Field(..., example="APP_ENV", description="環境設定のキーコード")
    values: str = Field(..., example="production", description="キーコードに対応する値")
    created_by: str = Field(..., example="admin", description="エントリを作成したユーザー")
    updated_by: str | None = Field(None, example="user123", description="エントリを更新したユーザー")
    created_at: datetime = Field(..., example="2024-11-16T12:00:00Z", description="エントリの作成日時 (ISO 8601形式)")
    updated_at: datetime | None = Field(
        None, example="2024-11-17T12:00:00Z", description="エントリの更新日時 (ISO 8601形式)"
    )

    class Config:
        orm_mode = True
        from_attributes = True  # from_ormを使うために必要
        # datetimeをISOフォーマットに変換
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
