import argparse
import datetime
import json
import random
import uuid
from pathlib import Path

import ai_client

BASE_DIR = Path(__file__).parent
PENDING_DIR = BASE_DIR / "drafts" / "pending"
PUBLISHED_DIR = BASE_DIR / "drafts" / "published"


def _recent_titles(limit: int = 8) -> list[str]:
    titles = []
    if not PUBLISHED_DIR.exists():
        return titles
    dirs = sorted(PUBLISHED_DIR.iterdir(), key=lambda p: p.name, reverse=True)
    for d in dirs[:limit]:
        meta_file = d / "draft.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            titles.append(meta.get("title", ""))
    return titles


def generate(style: str | None = None, topic: str | None = None, facts: str | None = None) -> str:
    topic = topic or random.choice(ai_client.TOPICS)
    avoid_titles = _recent_titles()

    news = ai_client.generate_news(style=style, topic=topic, facts=facts, avoid_titles=avoid_titles)

    draft_id = f"{datetime.datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
    draft_dir = PENDING_DIR / draft_id
    draft_dir.mkdir(parents=True, exist_ok=True)

    image_path = draft_dir / "image.jpg"
    ai_client.generate_image(news["image_prompt"], image_path)

    meta = {
        "id": draft_id,
        "title": news["title"],
        "text": news["text"],
        "topic": topic,
        "style": news.get("style"),
        "created_at": datetime.datetime.now().isoformat(),
        "status": "pending",
    }
    (draft_dir / "draft.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return draft_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", default=None)
    parser.add_argument("--topic", default=None)
    parser.add_argument("--facts", default=None)
    args = parser.parse_args()

    draft_id = generate(style=args.style, topic=args.topic, facts=args.facts)
    print(f"Черновик создан: {draft_id}")


if __name__ == "__main__":
    main()
