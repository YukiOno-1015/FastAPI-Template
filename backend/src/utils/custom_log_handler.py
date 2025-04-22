#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import os
import shutil
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    定期ローテートと古いログの圧縮を行うハンドラ。

    - ログは 'when' + 'interval' 間隔でローテート
    - 'backupCount' 日以上経過した .log ファイルを自動で .gz 圧縮
    """

    def __init__(
        self,
        filename: str,
        when: str = "midnight",
        interval: int = 1,
        backupCount: int = 7,
        encoding: Optional[str] = None,
        delay: bool = False,
        utc: bool = False,
        atTime: Optional[datetime.time] = None,
    ):
        # ベースクラス初期化
        super().__init__(
            filename=filename,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            utc=utc,
            atTime=atTime,
        )

    def doRollover(self) -> None:
        """
        ログローテーション後に古いログを圧縮する。
        """
        # 通常のローテーション
        super().doRollover()
        # 古いログファイルの圧縮処理
        self._compress_old_logs(days=self.backupCount)

    def _compress_old_logs(self, days: int) -> None:
        """
        指定日数以上経過した .log ファイルを .gz に圧縮し、元ファイルを削除する。

        Args:
            days (int): 圧縮対象とする経過日数
        """
        now = datetime.now()
        log_dir = Path(self.baseFilename).parent

        for log_file in log_dir.glob(f"{Path(self.baseFilename).stem}*.log"):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if now - mtime >= timedelta(days=days):
                    self._compress_file(log_file)
            except Exception as e:
                print(f"[CompressionError] {log_file}: {e}")

    def _compress_file(self, file_path: Path) -> None:
        """
        単一のログファイルを GZIP 圧縮し、元ファイルを削除する。

        Args:
            file_path (Path): 圧縮対象のログファイルパス
        """
        compressed = file_path.with_suffix(file_path.suffix + ".gz")
        try:
            with file_path.open("rb") as f_in, gzip.open(compressed, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            file_path.unlink()  # 元ファイル削除
            print(f"[Compressed] {file_path.name} -> {compressed.name}")
        except Exception as e:
            print(f"[CompressFail] {file_path.name}: {e}")
