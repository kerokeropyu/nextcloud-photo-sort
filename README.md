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
- 分類カテゴリ名をそのままアルバム名として、Nextcloud Photosのアルバムへ
  WebDAV(MKCOL/COPY)でファイルを追加(アルバムが無ければ自動作成)
- 処理済みファイルのパスをJSONファイルに記録し、二重処理を防止
  (分類・アルバム追加のいずれかに失敗したファイルは記録せず、次回実行時に再試行)
- 1回実行して終了する設計(cronなどからの定期実行を想定。常駐ループはしない)

以下は未実装です:

- カテゴリ⇔アルバム名のマッピングの柔軟な設定化(現状は1対1のハードコード)
- systemdサービス化・cron設定ファイル自体の作成

## セットアップ

### 前提

- Python 3.11以上
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/)(`qwen2.5vl:7b` モデルをpull済みであること)
- rcloneでNASをWebDAVマウント済みであること
- Nextcloudのアプリパスワード(「設定」→「セキュリティ」→
  「新しいアプリパスワードを作成」で発行。通常のログインパスワードは使わない)

### インストール

```bash
uv sync
cp .env.example .env
```

`.env`にNextcloudの接続情報を設定してください(`.env`はgit管理対象外です):

```
NEXTCLOUD_URL=https://your-nextcloud.example.com
NEXTCLOUD_USER=your-username
NEXTCLOUD_APP_PASSWORD=your-app-password
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

未処理ファイルが大量にある状態(初回実行時など)で、実機での動作確認を
少数のファイルだけに絞りたい場合は `NCPS_MAX_FILES` で件数を制限できます
(更新日時が新しい順に処理されます)。

```bash
# 未処理ファイルのうち、最新3件だけ処理する
NCPS_MAX_FILES=3 uv run nextcloud-photo-sort
```

### アルバムへの追加

分類が成功すると、カテゴリ名と同名のNextcloud Photosアルバムへ
WebDAV COPYでファイルを追加します(アルバムが存在しなければMKCOLで
自動作成)。ローカルのマウントルート(`src/nextcloud_photo_sort/albums.py`
の`NAS_MOUNT_ROOT`、デフォルト`/mnt/nas-photos`)がNextcloudの
WebDAVファイルルート(`/remote.php/dav/files/<user>/`)と対応している
必要があります。

アルバム追加に失敗した場合(分類自体は成功していても)、そのファイルは
処理済みとして記録されず、次回実行時に再試行されます
(その際、分類も再実行されます)。

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

`scanner.py` / `state.py` / `main.py` の主要ロジック(拡張子フィルタ、
新規ファイル検出、二重処理防止、分類失敗時のリトライ、`NCPS_MAX_FILES`
による件数制限)はモック・一時ディレクトリを使ったpytestで自動検証
されています(実際のOllama/NASへの接続は不要)。実機(Ollama + rcloneマウント)
を使った最終確認をしたい場合は、上記の`NCPS_MAX_FILES=3`で少数件に絞って
実行してください。
