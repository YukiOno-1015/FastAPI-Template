import gzip
import os
import shutil
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(
        self,
        filename,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding=None,
        delay=False,
        utc=False,
        atTime=None,
    ):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)

    def doRollover(self):
        """
        ログローテーション後に7日以上経過した古いログを圧縮します。
        """
        super().doRollover()  # 基底クラスのローテーション処理を呼び出す

        # 古いログファイルを圧縮
        self.compress_old_logs()

    def compress_old_logs(self):
        """7日以上経過したログファイルを圧縮します。"""
        now = datetime.now()
        log_dir = Path(self.baseFilename).parent  # pathlibを使用してログディレクトリを取得

        for log_file in log_dir.glob("*.log"):  # 拡張子が.logのファイルを検索
            if log_file.suffix == ".gz":  # 圧縮済みのファイルはスキップ
                continue

            try:
                # ファイルの最終更新日時を確認
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if (now - file_mtime).days >= 7:
                    self.compress_log_file(log_file)
            except Exception as e:
                print(f"ファイル処理エラー: {log_file}: {e}")

    def compress_log_file(self, file_path):
        """1つのログファイルを.gzip形式で圧縮します。"""
        compressed_file = f"{file_path}.gz"
        try:
            print(f"圧縮中: {file_path}")
            with open(file_path, "rb") as f_in:
                with gzip.open(compressed_file, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(file_path)  # 元の未圧縮ファイルを削除
            print(f"圧縮完了: {file_path}")
        except Exception as e:
            print(f"圧縮失敗: {file_path}: {e}")
