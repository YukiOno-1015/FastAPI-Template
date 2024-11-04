from fastapi_camelcase import CamelModel
from datetime import datetime


class EnvironmentInfoSchema(CamelModel):
    """
    EnvironmentInfoモデルのスキーマ。
    レスポンス用のスキーマとして使用。
    """

    key_code: str
    values: str
    created_by: str
    updated_by: str = None
    created_at: datetime
    updated_at: datetime = None

    class Config:
        orm_mode = True
        from_attributes = True  # from_ormを使うために必要
        # datetimeをISOフォーマットに変換
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
