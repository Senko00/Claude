import datetime
import json
import uuid
from pathlib import Path

import ai_client

DRAFTS_DIR = Path(__file__).parent / "drafts" / "pending"


def main() -> None:
    news = ai_client.generate_news()

    draft_id = f"{datetime.datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
    draft_dir = DRAFTS_DIR / draft_id
    draft_dir.mkdir(parents=True, exist_ok=True)

    image_path = draft_dir / "image.jpg"
    ai_client.generate_image(news["image_prompt"], image_path)

    meta = {
        "id": draft_id,
        "title": news["title"],
        "text": news["text"],
        "created_at": datetime.datetime.now().isoformat(),
        "status": "pending",
    }
    (draft_dir / "draft.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Черновик создан: {draft_id}")


if __name__ == "__main__":
    main()
