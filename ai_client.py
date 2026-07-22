import json
import re
import urllib.parse
import uuid
from pathlib import Path

import requests

import config

GIGACHAT_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

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


def _ssl_verify():
    if config.GIGACHAT_CA_BUNDLE:
        return config.GIGACHAT_CA_BUNDLE
    if config.GIGACHAT_INSECURE_SSL:
        return False
    return True


def _get_access_token() -> str:
    if not config.GIGACHAT_API_KEY:
        raise RuntimeError("GIGACHAT_API_KEY не задан в .env")

    response = requests.post(
        GIGACHAT_AUTH_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {config.GIGACHAT_API_KEY}",
        },
        data={"scope": config.GIGACHAT_SCOPE},
        verify=_ssl_verify(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def generate_news() -> dict:
    token = _get_access_token()

    response = requests.post(
        GIGACHAT_API_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={
            "model": "GigaChat",
            "messages": [{"role": "user", "content": PROMPT}],
            "temperature": 0.9,
        },
        verify=_ssl_verify(),
        timeout=60,
    )
    response.raise_for_status()
    raw_text = response.json()["choices"][0]["message"]["content"]

    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def generate_image(prompt: str, out_path: Path) -> None:
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
    response = requests.get(
        url, params={"width": 1024, "height": 576, "nologo": "true"}, timeout=120
    )
    response.raise_for_status()
    out_path.write_bytes(response.content)
