# nextcloud-photo-sort

Nextcloud上のNAS写真を、ローカルLLM(Ollama + Qwen2.5-VL)で分類し、
Nextcloud Photosのアルバムへ自動振り分けするツール。

NASはrcloneでWebDAVマウントし、ローカルフォルダとして扱う想定です。

## 現状の機能

- NAS上の画像ファイル(jpg / png / webp)を再帰的に走査
- Ollama(Qwen2.5-VL)に画像を送信し、あらかじめ定義したカテゴリ
  (人物 / 風景 / 食事 / 書類 / スクリーンショット / その他)に分類
- 分類結果を標準出力に表示(動作確認用に先頭数件のみ処理)

以下は未実装です:

- 新規ファイル検出の監視スクリプト
- Nextcloud Photos Albums APIへの書き込み(自動振り分け)

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
