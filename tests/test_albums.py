from unittest.mock import MagicMock, patch

import pytest
import requests

from nextcloud_photo_sort.albums import (
    AlbumConfigError,
    add_file_to_album,
    ensure_album_exists,
)


def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEXTCLOUD_URL", "http://example.test")
    monkeypatch.setenv("NEXTCLOUD_USER", "testuser")
    monkeypatch.setenv("NEXTCLOUD_APP_PASSWORD", "testpass")


def _response(status_code: int) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.raise_for_status.side_effect = (
        requests.HTTPError(f"status {status_code}") if status_code >= 400 else None
    )
    return response


def test_ensure_album_exists_raises_when_config_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NEXTCLOUD_URL", raising=False)
    monkeypatch.delenv("NEXTCLOUD_USER", raising=False)
    monkeypatch.delenv("NEXTCLOUD_APP_PASSWORD", raising=False)

    with pytest.raises(AlbumConfigError):
        ensure_album_exists("テスト")


def test_ensure_album_exists_created(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    with patch("nextcloud_photo_sort.albums.requests.request", return_value=_response(201)) as m:
        ensure_album_exists("書類")

    assert m.call_args.args[0] == "MKCOL"
    assert "書類" in m.call_args.args[1] or "%E6%9B%B8%E9%A1%9E" in m.call_args.args[1]


def test_ensure_album_exists_already_exists_is_not_an_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_env(monkeypatch)
    with patch("nextcloud_photo_sort.albums.requests.request", return_value=_response(405)):
        ensure_album_exists("書類")  # 例外が出ないことを確認


def test_ensure_album_exists_other_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    with (
        patch("nextcloud_photo_sort.albums.requests.request", return_value=_response(500)),
        pytest.raises(requests.HTTPError),
    ):
        ensure_album_exists("書類")


def test_add_file_to_album_success(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    with patch(
        "nextcloud_photo_sort.albums.requests.request",
        side_effect=[_response(201), _response(201)],
    ) as m:
        add_file_to_album("/mnt/nas-photos/Photos/a.jpg", "書類")

    assert m.call_count == 2
    assert m.call_args_list[0].args[0] == "MKCOL"
    assert m.call_args_list[1].args[0] == "COPY"


def test_add_file_to_album_duplicate_is_not_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    with patch(
        "nextcloud_photo_sort.albums.requests.request",
        side_effect=[_response(405), _response(409)],
    ):
        add_file_to_album("/mnt/nas-photos/Photos/a.jpg", "書類")  # 例外が出ないことを確認


def test_add_file_to_album_other_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    with (
        patch(
            "nextcloud_photo_sort.albums.requests.request",
            side_effect=[_response(405), _response(403)],
        ),
        pytest.raises(requests.HTTPError),
    ):
        add_file_to_album("/mnt/nas-photos/Photos/a.jpg", "書類")
