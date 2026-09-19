import os
import time
from pathlib import Path

from nextcloud_photo_sort.scanner import find_image_files, find_new_image_files


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def test_find_image_files_filters_by_extension_and_recurses(tmp_path: Path) -> None:
    _touch(tmp_path / "a.jpg")
    _touch(tmp_path / "b.jpeg")
    _touch(tmp_path / "c.png")
    _touch(tmp_path / "d.webp")
    _touch(tmp_path / "sub" / "e.jpg")
    _touch(tmp_path / "ignore.txt")

    found = set(find_image_files(str(tmp_path)))

    assert found == {
        str(tmp_path / "a.jpg"),
        str(tmp_path / "b.jpeg"),
        str(tmp_path / "c.png"),
        str(tmp_path / "d.webp"),
        str(tmp_path / "sub" / "e.jpg"),
    }


def test_find_new_image_files_excludes_processed(tmp_path: Path) -> None:
    _touch(tmp_path / "a.jpg")
    _touch(tmp_path / "b.jpg")

    processed = {str(tmp_path / "a.jpg")}
    new_files = find_new_image_files(str(tmp_path), processed)

    assert new_files == [str(tmp_path / "b.jpg")]


def test_find_new_image_files_limit_returns_latest_by_mtime(tmp_path: Path) -> None:
    paths = [tmp_path / f"{i}.jpg" for i in range(5)]
    for i, path in enumerate(paths):
        _touch(path)
        mtime = time.time() + i  # 後のファイルほど新しくする
        os.utime(path, (mtime, mtime))

    newest_three = find_new_image_files(str(tmp_path), processed=set(), limit=3)

    assert newest_three == [str(paths[4]), str(paths[3]), str(paths[2])]
