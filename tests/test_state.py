import json
from pathlib import Path

from nextcloud_photo_sort.state import load_processed_files, save_processed_files


def test_load_processed_files_returns_empty_set_when_missing(tmp_path: Path) -> None:
    state_path = tmp_path / "processed.json"

    assert load_processed_files(state_path) == set()


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    state_path = tmp_path / "nested" / "processed.json"
    processed = {"/photos/a.jpg", "/photos/b.jpg"}

    save_processed_files(processed, state_path)

    assert load_processed_files(state_path) == processed


def test_load_processed_files_returns_empty_set_on_corrupted_json(tmp_path: Path) -> None:
    state_path = tmp_path / "processed.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text("{not valid json", encoding="utf-8")

    assert load_processed_files(state_path) == set()


def test_save_processed_files_is_readable_as_json_list(tmp_path: Path) -> None:
    state_path = tmp_path / "processed.json"

    save_processed_files({"/photos/a.jpg"}, state_path)

    data = json.loads(state_path.read_text(encoding="utf-8"))
    assert data == ["/photos/a.jpg"]
