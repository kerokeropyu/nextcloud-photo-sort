"""処理済みファイルの状態管理(JSON永続化)。"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = (
    Path.home() / ".local" / "state" / "nextcloud-photo-sort" / "processed_files.json"
)


def load_processed_files(state_path: Path = DEFAULT_STATE_PATH) -> set[str]:
    """処理済みファイルパスの集合を読み込む。存在しない/壊れている場合は空集合を返す。"""
    if not state_path.exists():
        return set()
    try:
        with state_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        logger.exception("状態ファイルの読み込みに失敗しました: %s", state_path)
        return set()
    return set(data)


def save_processed_files(processed: set[str], state_path: Path = DEFAULT_STATE_PATH) -> None:
    """処理済みファイルパスの集合をJSONファイルへ保存する(アトミック書き込み)。"""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = state_path.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(sorted(processed), f, ensure_ascii=False, indent=2)
    tmp_path.replace(state_path)
