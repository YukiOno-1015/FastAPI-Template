from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.environment_info import EnvironmentInfo
from schemas.environment_info import EnvironmentInfoSchema
from app_state import environment_info_static

class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environment_info(self) -> list[EnvironmentInfo]:
        """
        DBのEnvironmentInfo情報を取得する。

        Returns:
            list[EnvironmentInfo]: 環境情報のリスト。

        Raises:
            HTTPException: 環境情報が見つからない場合。
        """
        infos = self.db.query(EnvironmentInfo).all()
        if not infos:
            raise HTTPException(status_code=404, detail="Environment info not found in database.")
        return infos

    def get_environment_info_as_schema(self) -> list[EnvironmentInfoSchema]:
        """
        静的なenvironment_info_static情報をスキーマ形式で取得する。

        Returns:
            list[EnvironmentInfoSchema]: 環境情報のリスト（スキーマ形式）。

        Raises:
            HTTPException: 環境情報が見つからない場合。
        """
        if not environment_info_static:
            raise HTTPException(status_code=404, detail="No static environment info found.")

        return [self._convert_to_schema(info) for info in environment_info_static.values()]

    def _convert_to_schema(self, info: dict) -> EnvironmentInfoSchema:
        """
        環境情報の辞書をスキーマ形式に変換します。

        Args:
            info (dict): 環境情報の辞書。

        Returns:
            EnvironmentInfoSchema: スキーマ形式の環境情報。
        """
        return EnvironmentInfoSchema(
            key_code=info["key_code"],
            values=info["values"],
            created_by=info["created_by"],
            updated_by=info.get("updated_by"),
            created_at=info["created_at"],
            updated_at=info.get("updated_at"),
        )

    def get_environment_info_static(self, key_code: str) -> dict:
        """
        静的なenvironment_infoから指定したキーの値を取得する。

        Args:
            key_code (str): 取得するキーコード。

        Returns:
            dict: 対応する環境情報の辞書。

        Raises:
            HTTPException: キーコードに対応する値が見つからない場合。
        """
        value = environment_info_static.get(key_code)
        if not value:
            raise HTTPException(status_code=404, detail=f"Environment info not found for key_code: {key_code}")
        return value

    def update_environment_info_static(self) -> None:
        """
        データベースからEnvironmentInfoを取得し、静的なenvironment_info_staticを更新する。
        """
        infos = self.get_environment_info()
        environment_info_static.clear()
        environment_info_static.update({
            info.key_code: {
                "key_code": info.key_code,
                "values": info.values,
                "created_by": info.created_by,
                "updated_by": info.updated_by,
                "created_at": info.created_at,
                "updated_at": info.updated_at,
            }
            for info in infos
        })
