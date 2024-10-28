import os
import logging
import gzip
import shutil
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta


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
        super().__init__(
            filename, when, interval, backupCount, encoding, delay, utc, atTime
        )

    def doRollover(self):
        """
        Override the base class method to compress old log files that are older than 7 days.
        """
        super().doRollover()  # Call the base class rollover to rotate files

        # Compress log files older than 7 days
        self.compress_old_logs()

    def compress_old_logs(self):
        """Compress logs older than 7 days."""
        now = datetime.now()
        for filename in os.listdir(os.path.dirname(self.baseFilename)):
            file_path = os.path.join(os.path.dirname(self.baseFilename), filename)
            # Check if the file is older than 7 days
            if not filename.endswith(".log"):  # Ignore non-log files
                continue
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if (now - file_mtime).days >= 7:
                self.compress_log_file(file_path)

    def compress_log_file(self, file_path):
        """Compress a single log file to .gz"""
        compressed_file = file_path + ".gz"
        with open(file_path, "rb") as f_in:
            with gzip.open(compressed_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(file_path)  # Remove the original uncompressed file
