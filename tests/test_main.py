import json
from collections.abc import Callable
from pathlib import Path

import pytest

from nextcloud_photo_sort import main as main_module


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def _setup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    photo_root = tmp_path / "photos"
    state_path = tmp_path / "state" / "processed.json"
    photo_root.mkdir()
    monkeypatch.setattr(main_module, "PHOTO_ROOT", str(photo_root))
    monkeypatch.setattr(main_module, "STATE_PATH", state_path)
    # 実際のNextcloudへ接続しないよう、デフォルトでは何もしないスタブに差し替える
    monkeypatch.setattr(main_module, "add_file_to_album", lambda path, album: None)
    return photo_root, state_path


def _recording_classifier(calls: list[str], result: str = "その他") -> Callable[[str], str]:
    def _classify(path: str) -> str:
        calls.append(path)
        return result

    return _classify


def _failing_classifier(message: str = "mock failure") -> Callable[[str], str]:
    def _classify(path: str) -> str:
        raise RuntimeError(message)

    return _classify


def _recording_album_adder(calls: list[tuple[str, str]]) -> Callable[[str, str], None]:
    def _add(path: str, album: str) -> None:
        calls.append((path, album))

    return _add


def _failing_album_adder(message: str = "mock album failure") -> Callable[[str, str], None]:
    def _add(path: str, album: str) -> None:
        raise RuntimeError(message)

    return _add


def test_first_run_processes_all_new_files_and_persists_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    photo_root, state_path = _setup(monkeypatch, tmp_path)
    _touch(photo_root / "a.jpg")
    _touch(photo_root / "b.jpg")

    calls: list[str] = []
    monkeypatch.setattr(main_module, "classify_image", _recording_classifier(calls))

    main_module.main()

    assert sorted(calls) == sorted([str(photo_root / "a.jpg"), str(photo_root / "b.jpg")])
    saved = json.loads(state_path.read_text(encoding="utf-8"))
    assert sorted(saved) == sorted(calls)


def test_second_run_finds_no_new_files(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    photo_root, _state_path = _setup(monkeypatch, tmp_path)
    _touch(photo_root / "a.jpg")

    calls: list[str] = []
    monkeypatch.setattr(main_module, "classify_image", _recording_classifier(calls))

    main_module.main()
    calls.clear()
    main_module.main()

    assert calls == []


def test_new_file_added_between_runs_is_detected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    photo_root, _state_path = _setup(monkeypatch, tmp_path)
    _touch(photo_root / "a.jpg")

    calls: list[str] = []
    monkeypatch.setattr(main_module, "classify_image", _recording_classifier(calls))

    main_module.main()
    calls.clear()

    _touch(photo_root / "b.jpg")
    main_module.main()

    assert calls == [str(photo_root / "b.jpg")]


def test_classification_failure_is_skipped_and_retried_next_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    photo_root, state_path = _setup(monkeypatch, tmp_path)
    _touch(photo_root / "a.jpg")

    monkeypatch.setattr(main_module, "classify_image", _failing_classifier())
    main_module.main()

    assert not state_path.exists()

    calls: list[str] = []
    monkeypatch.setattr(main_module, "classify_image", _recording_classifier(calls))
    main_module.main()

    assert calls == [str(photo_root / "a.jpg")]
    saved = json.loads(state_path.read_text(encoding="utf-8"))
    assert saved == [str(photo_root / "a.jpg")]


def test_max_files_limits_batch_to_latest_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    photo_root, _state_path = _setup(monkeypatch, tmp_path)
    for i in range(5):
        _touch(photo_root / f"{i}.jpg")

    monkeypatch.setenv(main_module.MAX_FILES_ENV, "2")
    calls: list[str] = []
    monkeypatch.setattr(main_module, "classify_image", _recording_classifier(calls))

    main_module.main()

    assert len(calls) == 2


def test_classified_file_is_added_to_album_named_after_category(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    photo_root, _state_path = _setup(monkeypatch, tmp_path)
    _touch(photo_root / "a.jpg")

    monkeypatch.setattr(main_module, "classify_image", _recording_classifier([], result="書類"))
    album_calls: list[tuple[str, str]] = []
    monkeypatch.setattr(main_module, "add_file_to_album", _recording_album_adder(album_calls))

    main_module.main()

    assert album_calls == [(str(photo_root / "a.jpg"), "書類")]


def test_album_add_failure_is_skipped_and_retried_next_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    photo_root, state_path = _setup(monkeypatch, tmp_path)
    _touch(photo_root / "a.jpg")

    monkeypatch.setattr(main_module, "classify_image", _recording_classifier([]))
    monkeypatch.setattr(main_module, "add_file_to_album", _failing_album_adder())
    main_module.main()

    assert not state_path.exists()

    album_calls: list[tuple[str, str]] = []
    monkeypatch.setattr(main_module, "add_file_to_album", _recording_album_adder(album_calls))
    main_module.main()

    assert album_calls == [(str(photo_root / "a.jpg"), "その他")]
    saved = json.loads(state_path.read_text(encoding="utf-8"))
    assert saved == [str(photo_root / "a.jpg")]
