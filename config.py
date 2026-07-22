import os

from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.environ.get("VK_TOKEN")
VK_GROUP_ID = os.environ.get("VK_GROUP_ID")

GIGACHAT_API_KEY = os.environ.get("GIGACHAT_API_KEY")
GIGACHAT_SCOPE = os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
GIGACHAT_CA_BUNDLE = os.environ.get("GIGACHAT_CA_BUNDLE")
GIGACHAT_INSECURE_SSL = os.environ.get("GIGACHAT_INSECURE_SSL", "false").lower() == "true"

BITRIX_WEBHOOK_URL = os.environ.get("BITRIX_WEBHOOK_URL")
BITRIX_IBLOCK_ID = os.environ.get("BITRIX_IBLOCK_ID")
