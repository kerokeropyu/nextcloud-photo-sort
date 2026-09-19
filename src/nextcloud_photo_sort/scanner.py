"""NAS上の画像ファイルのスキャン処理。"""

import glob

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


def find_image_files(root: str) -> list[str]:
    """rootディレクトリ以下から対応拡張子の画像ファイルを再帰的に列挙する。"""
    files: list[str] = []
    for ext in IMAGE_EXTENSIONS:
        files.extend(glob.glob(f"{root}/**/*.{ext}", recursive=True))
    return files


def find_new_image_files(root: str, processed: set[str]) -> list[str]:
    """rootディレクトリ以下から、processedに含まれない(未処理の)画像ファイルを列挙する。"""
    return [path for path in find_image_files(root) if path not in processed]
