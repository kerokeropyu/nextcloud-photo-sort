"""Ollama(Qwen2.5-VL)を使った画像分類ロジック。"""

import base64
import io

import ollama
from PIL import Image

CATEGORIES = ["人物", "風景", "食事", "書類", "スクリーンショット", "その他"]

DEFAULT_MODEL = "qwen2.5vl:7b"

CLASSIFY_PROMPT = (
    "この画像を次のカテゴリのいずれかに分類し、カテゴリ名のみ返答してください: "
    + ", ".join(CATEGORIES)
)


def encode_image(path: str, max_size: int = 1024) -> str:
    """画像を縮小・JPEG化してbase64文字列にエンコードする。"""
    img = Image.open(path)
    img.thumbnail((max_size, max_size))
    rgb_img = img.convert("RGB") if img.mode != "RGB" else img
    buf = io.BytesIO()
    rgb_img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def classify_image(path: str, model: str = DEFAULT_MODEL) -> str:
    """画像を分類し、カテゴリ名を返す。失敗時は例外を送出する(呼び出し元で処理)。"""
    img_b64 = encode_image(path)
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": CLASSIFY_PROMPT,
                "images": [img_b64],
            }
        ],
        options={"num_ctx": 8192},
    )
    content = response["message"]["content"]
    return str(content).strip()
