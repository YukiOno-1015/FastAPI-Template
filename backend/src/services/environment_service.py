"""
EnvironmentService: ビジネスロジックとキャッシュ管理を担当。
リポジトリを利用してDBアクセスし、静的キャッシュ(environment_info_static)を更新・参照します。
"""

import logging
from typing import Any, Dict, List

from fastapi import HTTPException

from app_state import environment_info_static
from repositories.environment_repository import EnvironmentRepository
from schemas.environment_info import EnvironmentInfoSchema
from utils.protocol import get_environment_value, handle_exception

# Uvicornの標準ロガーを取得
LOGGER = logging.getLogger("uvicorn")


class EnvironmentService:
    """
    環境情報に関するビジネスサービス。
    """

    def __init__(self, repository: EnvironmentRepository):
        """
        Args:
            repository (EnvironmentRepository): DBリポジトリ
        """
        self.repository = repository

    def get_all(self) -> List[EnvironmentInfoSchema]:
        """
        DBから全件取得し、スキーマ変換して返却します。

        Returns:
            List[EnvironmentInfoSchema]: 環境情報リスト

        Raises:
            HTTPException: データが0件の場合
        """
        infos = self.repository.fetch_all()
        if not infos:
            LOGGER.warning("[Service] 環境情報がDBにありません")
            # protocol.handle_exception を利用して例外を統一
            handle_exception(
                message="環境情報が存在しません。",
                exception=HTTPException(status_code=404, detail="環境情報が見つかりません。"),
            )
        # ORM → Pydantic スキーマ変換
        result = [EnvironmentInfoSchema.from_orm(info) for info in infos]
        LOGGER.info(f"[Service] {len(result)}件の情報を返却")
        return result

    def refresh_cache(self) -> None:
        """
        DBから全件取得し、静的キャッシュを更新します。
        """
        infos = self.repository.fetch_all()
        environment_info_static.clear()
        for info in infos:
            environment_info_static[info.key_code] = {
                "key_code": info.key_code,
                "values": info.values,
                "created_by": info.created_by,
                "updated_by": info.updated_by,
                "created_at": info.created_at,
                "updated_at": info.updated_at,
            }
        LOGGER.info(f"[Service] キャッシュを{len(infos)}件更新しました")

    def get_value(self, key_code: str) -> str:
        """
        静的キャッシュから指定キーの値を取得します。

        Args:
            key_code (str): キーコード

        Returns:
            str: 該当する環境値

        Raises:
            HTTPException: キャッシュにキーがない場合
        """
        # protocol.get_environment_value を利用
        return get_environment_value(key_code)
