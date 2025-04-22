#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ArgumentError

# Uvicorn など上位ロガーを継承
logger = logging.getLogger("uvicorn.database")  # 'uvicorn' 下にデータベース用ロガー

# .envのロード（本モジュール読み込み時に一度だけ）
load_dotenv()


def get_database_url() -> str:
    """
    環境変数から DATABASE_URL を取得し、未設定時は例外を投げます。

    Returns:
        str: DATABASE_URL の文字列

    Raises:
        RuntimeError: 環境変数が設定されていない場合
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        logger.error("環境変数 'DATABASE_URL' が設定されていません。")
        raise RuntimeError("環境変数 'DATABASE_URL' が設定されていません。")
    logger.debug(f"取得した DATABASE_URL: {url}")
    return url


def create_db_engine(echo: bool = False) -> Engine:
    """
    SQLAlchemy エンジンを生成します。

    Args:
        echo (bool): SQL の発行ログを標準出力に出すかどうか

    Returns:
        Engine: 作成された DB エンジン

    Raises:
        RuntimeError: エンジン生成時に引数エラーが発生した場合
    """
    url = get_database_url()
    try:
        engine = create_engine(url, echo=echo, future=True)
        logger.info("データベースエンジンを正常に作成しました。")
        return engine
    except ArgumentError as e:
        logger.error(f"データベースエンジンの作成に失敗しました: {e}", exc_info=True)
        raise RuntimeError(f"データベースエンジンの作成に失敗しました: {e}") from e


# モジュール読み込み時にエンジンを作成
engine = create_db_engine(echo=True)
