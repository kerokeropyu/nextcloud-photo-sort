"""エントリーポイント: NAS上の写真を分類してカテゴリを表示する。"""

import glob
from datetime import datetime

from nextcloud_photo_sort.classifier import classify_image

PHOTO_ROOT = "/mnt/nas-photos/Photos"
IMAGE_EXTENSIONS = ["jpg", "png", "webp"]

# 動作確認用に先頭N件のみ処理する(監視・全件処理はまだ実装しない)
PREVIEW_LIMIT = 10


def find_image_files(root: str) -> list[str]:
    """rootディレクトリ以下から対応拡張子の画像ファイルを再帰的に列挙する。"""
    files: list[str] = []
    for ext in IMAGE_EXTENSIONS:
        files.extend(glob.glob(f"{root}/**/*.{ext}", recursive=True))
    return files


def main() -> None:
    files = find_image_files(PHOTO_ROOT)

    for path in files[:PREVIEW_LIMIT]:
        start = datetime.now()
        print(f"開始: {start.strftime('%H:%M:%S')} - {path}")

        result = classify_image(path)

        end = datetime.now()
        elapsed = (end - start).total_seconds()
        print(f"終了: {end.strftime('%H:%M:%S')} (所要時間: {elapsed:.1f}秒)")
        print(f"→ 分類結果: {result}\n")


if __name__ == "__main__":
    main()
