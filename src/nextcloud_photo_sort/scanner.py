"""NAS上の画像ファイルのスキャン処理。"""

import glob
from pathlib import Path

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


def find_image_files(root: str) -> list[str]:
    """rootディレクトリ以下から対応拡張子の画像ファイルを再帰的に列挙する。"""
    files: list[str] = []
    for ext in IMAGE_EXTENSIONS:
        files.extend(glob.glob(f"{root}/**/*.{ext}", recursive=True))
    return files


def find_new_image_files(root: str, processed: set[str], limit: int | None = None) -> list[str]:
    """rootディレクトリ以下から、processedに含まれない(未処理の)画像ファイルを列挙する。

    limitを指定した場合、更新日時が新しい順に最大limit件だけ返す
    (未処理ファイルが大量にある実機での動作確認時に、全件処理を避けるため)。
    """
    new_files = [path for path in find_image_files(root) if path not in processed]
    if limit is None:
        return new_files
    new_files.sort(key=lambda p: Path(p).stat().st_mtime, reverse=True)
    return new_files[:limit]
