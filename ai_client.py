import json
import re
import urllib.parse
from pathlib import Path

import requests

import config

YANDEXGPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

THEMES = [
    "производство и выпуск новой техники",
    "отгрузка кранов заказчику",
    "новый крупный заказ",
    "модернизация оборудования на заводе",
    "участие в отраслевой выставке",
    "охрана труда и техника безопасности",
    "партнёрство с другим предприятием",
    "обучение и набор персонала",
]

PROMPT_TEMPLATE = """
Ты — SMM-редактор Симбирского кранового завода (производство башенных
и мостовых кранов). Придумай одну правдоподобную новость для соцсетей
и сайта завода.

Тема новости: {theme}.
{facts_block}{avoid_block}
Пиши ТОЛЬКО на русском языке, деловым стилем, без ошибок.

Ответь СТРОГО в виде JSON без markdown-разметки и пояснений:
{{
  "title": "короткий заголовок на русском",
  "text": "текст новости на 2-4 абзаца на русском",
  "image_prompt": "краткое описание картинки НА АНГЛИЙСКОМ для генератора изображений"
}}
"""


def _build_prompt(theme, facts, avoid_titles) -> str:
    theme = theme or "на твой выбор из жизни завода"

    facts_block = ""
    if facts:
        facts_block = (
            f"Используй только следующие факты, ничего не выдумывай сверх них:\n{facts}\n"
        )

    avoid_block = ""
    if avoid_titles:
        titles = "\n".join(f"- {t}" for t in avoid_titles)
        avoid_block = f"Не повторяй темы уже опубликованных новостей:\n{titles}\n"

    return PROMPT_TEMPLATE.format(theme=theme, facts_block=facts_block, avoid_block=avoid_block)


def generate_news(theme=None, facts=None, avoid_titles=None) -> dict:
    if not config.YANDEX_API_KEY or not config.YANDEX_FOLDER_ID:
        raise RuntimeError("YANDEX_API_KEY / YANDEX_FOLDER_ID не заданы в .env")

    prompt = _build_prompt(theme, facts, avoid_titles or [])

    response = requests.post(
        YANDEXGPT_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {config.YANDEX_API_KEY}",
            "x-folder-id": config.YANDEX_FOLDER_ID,
        },
        json={
            "modelUri": f"gpt://{config.YANDEX_FOLDER_ID}/{config.YANDEX_MODEL}/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.9,
                "maxTokens": "2000",
            },
            "messages": [{"role": "user", "text": prompt}],
        },
        timeout=60,
    )
    if not response.ok:
        raise RuntimeError(
            f"YandexGPT API вернул ошибку {response.status_code}: {response.text}"
        )
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
