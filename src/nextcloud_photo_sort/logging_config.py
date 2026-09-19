"""ロギング設定(ローテーション付きファイル出力 + コンソール出力)。"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

DEFAULT_LOG_DIR = Path.home() / ".local" / "state" / "nextcloud-photo-sort"
LOG_FILE_NAME = "nextcloud-photo-sort.log"
MAX_BYTES = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 5


def configure_logging(level: int = logging.INFO) -> None:
    """ルートロガーにローテーション付きファイルハンドラとコンソールハンドラを設定する。

    ログ出力先は環境変数 NCPS_LOG_DIR で上書き可能(デフォルトは
    ~/.local/state/nextcloud-photo-sort/nextcloud-photo-sort.log)。
    5MBを超えると世代ローテーションし、直近5世代を保持する。
    """
    log_dir = Path(os.environ.get("NCPS_LOG_DIR", str(DEFAULT_LOG_DIR)))
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_dir / LOG_FILE_NAME,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
