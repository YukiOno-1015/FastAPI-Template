from datetime import datetime

from sqlmodel import Column, DateTime, Field, SQLModel, String


class EnvironmentInfo(SQLModel, table=True):
    """
    環境情報マスタモデル。
    システム設定や環境情報を保存するためのテーブル。

    Attributes:
        key_code (str): 環境情報のキーコード。主キーであり、ユニークな値。
        values (str): 環境情報の値。必須項目。
        created_by (str): レコードの登録者の名前。必須項目。
        updated_by (str): レコードの更新者の名前。任意項目。
        created_at (datetime): レコードの登録日時。自動的に現在のUTC日時が設定されます。
        updated_at (datetime): レコードの更新日時。自動的に現在のUTC日時が設定されます。
    """

    __tablename__ = "environment_info"

    key_code: str = Field(sa_column=Column(String(length=50), primary_key=True, comment="環境情報のキーコード"))

    values: str = Field(sa_column=Column(String(length=255), nullable=False, comment="環境情報の値"))

    created_by: str = Field(sa_column=Column(String(length=50), nullable=False, comment="レコードの登録者"))
    updated_by: str = Field(sa_column=Column(String(length=50), nullable=True, comment="レコードの更新者"))
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, default=datetime.utcnow, comment="レコードの登録日時")
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=True, default=datetime.utcnow, comment="レコードの更新日時")
    )
