import base64

import requests


def post_news(endpoint_url: str, secret: str, iblock_id: str, title: str, text: str, image_path: str) -> dict:
    if not endpoint_url or not secret or not iblock_id:
        raise RuntimeError(
            "BITRIX_ENDPOINT_URL / BITRIX_ENDPOINT_SECRET / BITRIX_IBLOCK_ID не заданы в .env"
        )

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "secret": secret,
        "iblock_id": int(iblock_id),
        "title": title,
        "text": text,
        "image_base64": image_b64,
    }

    response = requests.post(endpoint_url, json=payload, timeout=60)
    if not response.ok:
        raise RuntimeError(
            f"Bitrix-эндпоинт вернул ошибку {response.status_code}: {response.text}"
        )
    data = response.json()
    if "error" in data:
        raise RuntimeError(f"Bitrix-эндпоинт вернул ошибку: {data}")
    return data["result"]
