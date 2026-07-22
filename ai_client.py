import json
import re
import urllib.parse
from pathlib import Path

import requests

import config

YANDEXGPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

PROMPT = """
Ты — SMM-редактор Симбирского кранового завода (производство башенных
и мостовых кранов). Придумай одну правдоподобную новость для соцсетей
и сайта завода: например о производстве, отгрузке техники, новом заказе,
модернизации оборудования, участии в выставке, охране труда и т.п.

Ответь СТРОГО в виде JSON без markdown-разметки и пояснений:
{
  "title": "короткий заголовок",
  "text": "текст новости на 2-4 абзаца, деловой стиль",
  "image_prompt": "краткое описание картинки на английском для генератора изображений"
}
"""


def generate_news() -> dict:
    if not config.YANDEX_API_KEY or not config.YANDEX_FOLDER_ID:
        raise RuntimeError("YANDEX_API_KEY / YANDEX_FOLDER_ID не заданы в .env")

    response = requests.post(
        YANDEXGPT_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {config.YANDEX_API_KEY}",
            "x-folder-id": config.YANDEX_FOLDER_ID,
        },
        json={
            "modelUri": f"gpt://{config.YANDEX_FOLDER_ID}/{config.YANDEX_MODEL}",
            "completionOptions": {
                "stream": False,
                "temperature": 0.9,
                "maxTokens": "2000",
            },
            "messages": [{"role": "user", "text": PROMPT}],
        },
        timeout=60,
    )
    response.raise_for_status()
    raw_text = response.json()["result"]["alternatives"][0]["message"]["text"]

    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def generate_image(prompt: str, out_path: Path) -> None:
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
    response = requests.get(
        url, params={"width": 1024, "height": 576, "nologo": "true"}, timeout=120
    )
    response.raise_for_status()
    out_path.write_bytes(response.content)
