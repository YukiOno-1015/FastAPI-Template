"""
EnvironmentRepository: 環境情報の永続化レイヤを担当。
DBからの読み書き(CRUD)を集約し、他層から直接DBに触れないようにします。
"""

import logging
from typing import List

from sqlalchemy.orm import Session

from models.environment_info import EnvironmentInfo

# Uvicornの標準ロガーを取得
LOGGER = logging.getLogger("uvicorn")


class EnvironmentRepository:
    """
    環境情報テーブルへのアクセスリポジトリ。
    """

    def __init__(self, db: Session):
        """
        Args:
            db (Session): SQLAlchemy/SQLModel セッション
        """
        self.db = db

    def fetch_all(self) -> List[EnvironmentInfo]:
        """
        全レコードを取得します。

        Returns:
            List[EnvironmentInfo]: 取得結果リスト
        """
        infos = self.db.query(EnvironmentInfo).all()
        LOGGER.debug(f"[Repository] DBから{len(infos)}件取得")
        return infos

    def find_by_key(self, key_code: str) -> EnvironmentInfo | None:
        """
        キーコードで単一レコードを取得します。

        Args:
            key_code (str): 検索キー

        Returns:
            EnvironmentInfo | None: レコードまたはNone
        """
        info = self.db.query(EnvironmentInfo).filter(EnvironmentInfo.key_code == key_code).first()
        LOGGER.debug(f"[Repository] key_code={key_code} 取得結果: {info is not None}")
        return info
