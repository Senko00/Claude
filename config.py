import os

from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.environ.get("VK_TOKEN")
VK_GROUP_ID = os.environ.get("VK_GROUP_ID")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct")

BITRIX_ENDPOINT_URL = os.environ.get("BITRIX_ENDPOINT_URL")
BITRIX_ENDPOINT_SECRET = os.environ.get("BITRIX_ENDPOINT_SECRET")
BITRIX_IBLOCK_ID = os.environ.get("BITRIX_IBLOCK_ID")
