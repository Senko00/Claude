import json
import shutil
import webbrowser
from pathlib import Path
from threading import Timer

from flask import Flask, flash, redirect, render_template, request, url_for

import ai_client
import generator
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
    return render_template(
        "index.html", drafts=load_drafts(), styles=ai_client.STYLES, topics=ai_client.TOPICS
    )


@app.route("/generate", methods=["POST"])
def generate():
    style = request.form.get("style") or None
    topic = request.form.get("topic") or None
    facts = request.form.get("facts") or None
    try:
        draft_id = generator.generate(style=style, topic=topic, facts=facts)
        flash(f"Новый черновик «{draft_id}» готов, проверьте его ниже")
    except Exception as exc:  # noqa: BLE001 - показываем любую ошибку генерации редактору
        flash(f"Ошибка генерации: {exc}")
    return redirect(url_for("index"))


@app.route("/draft/<draft_id>/image", methods=["POST"])
def replace_image(draft_id: str):
    draft_dir = PENDING_DIR / draft_id
    file = request.files.get("image")
    if not file or file.filename == "":
        flash("Файл не выбран")
        return redirect(url_for("index"))
    file.save(draft_dir / "image.jpg")
    flash(f"Картинка для «{draft_id}» заменена")
    return redirect(url_for("index"))


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
    Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(debug=False, port=5000)
