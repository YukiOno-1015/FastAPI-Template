"""
データベースセッション管理モジュール
- SQLAlchemy エンジンからセッションを生成
- 依存注入可能なジェネレータ関数を提供
"""

import logging
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from .connection import engine

# Uvicornロガーを使用
LOGGER = logging.getLogger("uvicorn.database")

# セッションファクトリの生成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)  # SQLAlchemy 2.0 スタイル


def get_session() -> Generator[Session, None, None]:
    """
    データベースセッションを生成し、リクエスト終了後にクローズします。

    Yields:
        Session: SQLAlchemy セッションインスタンス
    """
    session: Session = SessionLocal()
    try:
        yield session
    except Exception as exc:
        LOGGER.error(f"[DB] セッション使用中にエラーが発生しました: {exc}", exc_info=True)
        session.rollback()
        raise
    finally:
        session.close()
        LOGGER.debug("[DB] セッションをクローズしました")
