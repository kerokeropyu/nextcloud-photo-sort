"""Nextcloud PhotosアルバムへのWebDAV連携(MKCOL/COPY)。

curlでの動作確認結果(2026-09-20):
- MKCOL: 新規作成は201、既存コレクションへのMKCOLは405 Method Not Allowed
- COPY: 新規追加は201、既にアルバムに追加済みのファイルへのCOPYは409 Conflict
"""

import logging
import os
from pathlib import PurePosixPath
from urllib.parse import quote

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# rcloneでマウントしたNASのローカルルート
# (Nextcloud WebDAVファイルルート /remote.php/dav/files/<user>/ に対応)
NAS_MOUNT_ROOT = "/mnt/nas-photos"

_REQUEST_TIMEOUT = 30


class AlbumConfigError(RuntimeError):
    """Nextcloud接続情報(環境変数/.env)が不足している場合の例外。"""


def _env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise AlbumConfigError(f"環境変数 {name} が設定されていません(.envを確認してください)")
    return value


def _auth() -> tuple[str, str]:
    return _env("NEXTCLOUD_USER"), _env("NEXTCLOUD_APP_PASSWORD")


def _album_collection_url(album: str) -> str:
    base = _env("NEXTCLOUD_URL").rstrip("/")
    user = _env("NEXTCLOUD_USER")
    return f"{base}/remote.php/dav/photos/{user}/albums/{quote(album)}/"


def _file_url(local_path: str) -> str:
    base = _env("NEXTCLOUD_URL").rstrip("/")
    user = _env("NEXTCLOUD_USER")
    relative = PurePosixPath(local_path).relative_to(NAS_MOUNT_ROOT)
    return f"{base}/remote.php/dav/files/{user}/{quote(str(relative))}"


def ensure_album_exists(album: str) -> None:
    """アルバム(コレクション)が無ければMKCOLで作成する。

    既存コレクションへのMKCOLは405が返るため、既に存在するとみなして無視する。
    """
    url = _album_collection_url(album)
    response = requests.request("MKCOL", url, auth=_auth(), timeout=_REQUEST_TIMEOUT)
    if response.status_code == 201:
        logger.info("アルバムを作成しました: %s", album)
        return
    if response.status_code == 405:
        logger.debug("アルバムは既に存在します: %s", album)
        return
    response.raise_for_status()


def add_file_to_album(local_path: str, album: str) -> None:
    """local_pathのファイルを、album名のアルバムへWebDAV COPYで追加する。

    既に同じアルバムに追加済みの場合は409が返るため、エラーとして扱わず無視する。
    """
    ensure_album_exists(album)

    filename = PurePosixPath(local_path).name
    source_url = _file_url(local_path)
    destination_url = f"{_album_collection_url(album)}{quote(filename)}"

    response = requests.request(
        "COPY",
        source_url,
        auth=_auth(),
        headers={"Destination": destination_url},
        timeout=_REQUEST_TIMEOUT,
    )
    if response.status_code in (201, 204):
        logger.info("アルバムへ追加しました: %s → %s", local_path, album)
        return
    if response.status_code == 409:
        logger.info("既にアルバムに追加済みのためスキップ: %s → %s", local_path, album)
        return
    response.raise_for_status()
