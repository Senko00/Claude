import json
import shutil
from pathlib import Path

from flask import Flask, flash, redirect, render_template, url_for

import publisher

BASE_DIR = Path(__file__).parent
PENDING_DIR = BASE_DIR / "drafts" / "pending"
PUBLISHED_DIR = BASE_DIR / "drafts" / "published"
REJECTED_DIR = BASE_DIR / "drafts" / "rejected"

app = Flask(__name__, static_folder=str(BASE_DIR / "drafts"), static_url_path="/drafts")
app.secret_key = "local-dev-only"


def load_drafts() -> list:
    drafts = []
    for d in sorted(PENDING_DIR.iterdir()):
        meta_file = d / "draft.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            meta["dir"] = d.name
            drafts.append(meta)
    return drafts


@app.route("/")
def index():
    return render_template("index.html", drafts=load_drafts())


@app.route("/draft/<draft_id>/approve", methods=["POST"])
def approve(draft_id: str):
    draft_dir = PENDING_DIR / draft_id
    try:
        publisher.publish(draft_dir)
    except Exception as exc:  # noqa: BLE001 - показываем любую ошибку публикации редактору
        flash(f"Ошибка публикации «{draft_id}»: {exc}")
        return redirect(url_for("index"))

    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(draft_dir), str(PUBLISHED_DIR / draft_id))
    flash(f"Новость «{draft_id}» опубликована в VK и на сайте")
    return redirect(url_for("index"))


@app.route("/draft/<draft_id>/reject", methods=["POST"])
def reject(draft_id: str):
    draft_dir = PENDING_DIR / draft_id
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(draft_dir), str(REJECTED_DIR / draft_id))
    flash(f"Новость «{draft_id}» отклонена")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
