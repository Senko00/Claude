import base64

import requests


def post_news(webhook_url: str, iblock_id: str, title: str, text: str, image_path: str) -> dict:
    if not webhook_url or not iblock_id:
        raise RuntimeError("BITRIX_WEBHOOK_URL / BITRIX_IBLOCK_ID не заданы в .env")

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    fields = {
        "IBLOCK_ID": iblock_id,
        "NAME": title,
        "ACTIVE": "Y",
        "PREVIEW_TEXT": text[:255],
        "DETAIL_TEXT": text,
        "DETAIL_TEXT_TYPE": "text",
        "PREVIEW_PICTURE": {"fileData": ["cover.jpg", image_b64]},
        "DETAIL_PICTURE": {"fileData": ["cover.jpg", image_b64]},
    }

    url = webhook_url.rstrip("/") + "/iblock.element.add.json"
    response = requests.post(url, json={"fields": fields}, timeout=60)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(f"Bitrix REST error: {data}")
    return data["result"]
