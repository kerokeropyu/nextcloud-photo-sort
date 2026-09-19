"""エントリーポイント: NAS上の写真を分類してカテゴリを表示する。"""

import glob
import logging
from datetime import datetime

from nextcloud_photo_sort.classifier import classify_image
from nextcloud_photo_sort.logging_config import configure_logging

logger = logging.getLogger(__name__)

PHOTO_ROOT = "/mnt/nas-photos/Photos"
IMAGE_EXTENSIONS = ["jpg", "png", "webp"]

# 動作確認用に先頭N件のみ処理する(監視・全件処理はまだ実装しない)
PREVIEW_LIMIT = 100


def find_image_files(root: str) -> list[str]:
    """rootディレクトリ以下から対応拡張子の画像ファイルを再帰的に列挙する。"""
    files: list[str] = []
    for ext in IMAGE_EXTENSIONS:
        files.extend(glob.glob(f"{root}/**/*.{ext}", recursive=True))
    return files


def main() -> None:
    configure_logging()

    files = find_image_files(PHOTO_ROOT)
    logger.info("対象ファイル数: %d件(先頭%d件を処理)", len(files), PREVIEW_LIMIT)

    for path in files[:PREVIEW_LIMIT]:
        start = datetime.now()
        logger.info("分類開始: %s", path)

        result = classify_image(path)

        elapsed = (datetime.now() - start).total_seconds()
        logger.info("分類完了 (所要時間: %.1f秒) → %s: %s", elapsed, path, result)


if __name__ == "__main__":
    main()
