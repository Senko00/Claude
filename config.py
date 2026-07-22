import os

from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.environ.get("VK_TOKEN")
VK_GROUP_ID = os.environ.get("VK_GROUP_ID")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

BITRIX_WEBHOOK_URL = os.environ.get("BITRIX_WEBHOOK_URL")
BITRIX_IBLOCK_ID = os.environ.get("BITRIX_IBLOCK_ID")
