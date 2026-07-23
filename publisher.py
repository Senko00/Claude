import json
from pathlib import Path

import bitrix_client
import config
import vk_client


def publish(draft_dir: Path) -> None:
    meta = json.loads((draft_dir / "draft.json").read_text(encoding="utf-8"))
    image_path = draft_dir / "image.jpg"

    bitrix_result = bitrix_client.post_news(
        config.BITRIX_ENDPOINT_URL,
        config.BITRIX_ENDPOINT_SECRET,
        config.BITRIX_IBLOCK_ID,
        meta["title"],
        meta["text"],
        str(image_path),
    )
    article_url = bitrix_result.get("URL")

    vk_client.post_news(
        config.VK_TOKEN,
        config.VK_GROUP_ID,
        meta["title"],
        meta["text"],
        image_path=str(image_path),
        link=article_url,
    )
