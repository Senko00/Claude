import os

from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.environ.get("VK_TOKEN")
VK_GROUP_ID = os.environ.get("VK_GROUP_ID")

YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID")
YANDEX_MODEL = os.environ.get("YANDEX_MODEL", "yandexgpt-lite")

BITRIX_WEBHOOK_URL = os.environ.get("BITRIX_WEBHOOK_URL")
BITRIX_IBLOCK_ID = os.environ.get("BITRIX_IBLOCK_ID")
