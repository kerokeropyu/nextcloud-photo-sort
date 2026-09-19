# nextcloud-photo-sort

Nextcloud上のNAS写真を、ローカルLLM(Ollama + Qwen2.5-VL)で分類し、
Nextcloud Photosのアルバムへ自動振り分けするツール。

NASはrcloneでWebDAVマウントし、ローカルフォルダとして扱う想定です。

## 現状の機能

- NAS上の画像ファイル(jpg / jpeg / png / webp)を再帰的に走査し、
  未処理(新規)のファイルのみを検出
- Ollama(Qwen2.5-VL)に画像を送信し、あらかじめ定義したカテゴリ
  (人物 / 風景 / 食事 / 書類 / スクリーンショット / その他)に分類
- 分類結果をログに記録
- 処理済みファイルのパスをJSONファイルに記録し、二重処理を防止
  (分類に失敗したファイルは記録せず、次回実行時に再試行)
- 1回実行して終了する設計(cronなどからの定期実行を想定。常駐ループはしない)

以下は未実装です:

- Nextcloud Photos Albums APIへの書き込み(自動振り分け)
- systemdサービス化・cron設定ファイル自体の作成

## セットアップ

### 前提

- Python 3.11以上
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/)(`qwen2.5vl:7b` モデルをpull済みであること)
- rcloneでNASをWebDAVマウント済みであること

### インストール

```bash
uv sync
```

## 実行方法

`src/nextcloud_photo_sort/main.py` の `PHOTO_ROOT` を、rcloneでマウントした
写真ディレクトリのパスに合わせて変更してください(デフォルトは
`/mnt/nas-photos/Photos`)。

```bash
uv run nextcloud-photo-sort
```

実行のたびに`PHOTO_ROOT`以下を走査し、処理済みファイル一覧
(`~/.local/state/nextcloud-photo-sort/processed_files.json`)に無い
ファイルだけを分類します。cronなどで定期的に実行することを想定しています
(このツール自体はループせず、1回実行して終了します)。

### ログ

実行ログはコンソール出力に加えて、以下のファイルにもローテーション付きで
書き込まれます(5MBを超えると世代ローテーションし、直近5世代を保持)。

- デフォルト: `~/.local/state/nextcloud-photo-sort/nextcloud-photo-sort.log`
- 環境変数 `NCPS_LOG_DIR` でディレクトリを上書き可能

```bash
NCPS_LOG_DIR=/var/log/nextcloud-photo-sort uv run nextcloud-photo-sort
```

## 開発

```bash
# Lint / Format
uv run ruff check .
uv run ruff format .

# 型チェック
uv run mypy

# テスト
uv run pytest
```
