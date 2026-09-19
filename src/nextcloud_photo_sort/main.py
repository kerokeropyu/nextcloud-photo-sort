"""エントリーポイント: NAS上の新規写真を分類してログに記録する。

cron等から1回だけ実行される想定(常駐ループはしない)。
"""

import logging
import os

from nextcloud_photo_sort.classifier import classify_image
from nextcloud_photo_sort.logging_config import configure_logging
from nextcloud_photo_sort.scanner import find_new_image_files
from nextcloud_photo_sort.state import (
    DEFAULT_STATE_PATH,
    load_processed_files,
    save_processed_files,
)

logger = logging.getLogger(__name__)

PHOTO_ROOT = "/mnt/nas-photos/Photos"
STATE_PATH = DEFAULT_STATE_PATH

# 1回の実行あたりの処理件数上限。環境変数 NCPS_MAX_FILES で指定可能
# (指定時は更新日時が新しい順に処理する。未処理ファイルが大量にある
# 状態での動作確認時に、全件処理を避けるために使う)
MAX_FILES_ENV = "NCPS_MAX_FILES"


def _get_max_files() -> int | None:
    value = os.environ.get(MAX_FILES_ENV)
    return int(value) if value else None


def main() -> None:
    configure_logging()

    processed = load_processed_files(STATE_PATH)
    new_files = find_new_image_files(PHOTO_ROOT, processed, limit=_get_max_files())
    logger.info("新規ファイル数: %d件", len(new_files))

    for path in new_files:
        try:
            result = classify_image(path)
        except Exception:
            logger.exception("分類に失敗したためスキップします(次回再試行): %s", path)
            continue

        logger.info("分類完了 → %s: %s", path, result)
        processed.add(path)
        save_processed_files(processed, STATE_PATH)


if __name__ == "__main__":
    main()
