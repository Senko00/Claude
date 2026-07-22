import json
import re
import urllib.parse
from pathlib import Path

import requests

import config

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

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
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY не задан в .env")

    response = requests.post(
        f"{GEMINI_URL}?key={config.GEMINI_API_KEY}",
        json={"contents": [{"parts": [{"text": PROMPT}]}]},
        timeout=60,
    )
    response.raise_for_status()
    raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def generate_image(prompt: str, out_path: Path) -> None:
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
    response = requests.get(
        url, params={"width": 1024, "height": 576, "nologo": "true"}, timeout=120
    )
    response.raise_for_status()
    out_path.write_bytes(response.content)
