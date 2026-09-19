"""エントリーポイント: NAS上の新規写真を分類してログに記録する。

cron等から1回だけ実行される想定(常駐ループはしない)。
"""

import logging

from nextcloud_photo_sort.classifier import classify_image
from nextcloud_photo_sort.logging_config import configure_logging
from nextcloud_photo_sort.scanner import find_new_image_files
from nextcloud_photo_sort.state import load_processed_files, save_processed_files

logger = logging.getLogger(__name__)

PHOTO_ROOT = "/mnt/nas-photos/Photos"


def main() -> None:
    configure_logging()

    processed = load_processed_files()
    new_files = find_new_image_files(PHOTO_ROOT, processed)
    logger.info("新規ファイル数: %d件", len(new_files))

    for path in new_files:
        try:
            result = classify_image(path)
        except Exception:
            logger.exception("分類に失敗したためスキップします(次回再試行): %s", path)
            continue

        logger.info("分類完了 → %s: %s", path, result)
        processed.add(path)
        save_processed_files(processed)


if __name__ == "__main__":
    main()
