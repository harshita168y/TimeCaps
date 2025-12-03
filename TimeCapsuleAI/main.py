from __future__ import annotations

from pathlib import Path
from datetime import date, datetime

from app.media_processing.loader import load_day_media
from app.media_processing.vision import caption_day_media
from app.story_engine.story_generator import build_day_story
from app.story_engine.trailer_script import build_trailer_script
from app.video_composer.composer import render_trailer
from fastapi import UploadFile, File

# 🔥 Use the SAME folder Flutter uses
MEDIA_ROOT = Path("day_media")
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)


STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)


def get_day_dir(day: str | None = None) -> Path:
    if day is None:
        day = date.today().isoformat()
    d = MEDIA_ROOT / day
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_wrapup_output_path(day: str | None = None) -> Path:
    if day is None:
        day = date.today().isoformat()
    return STATIC_DIR / f"timecapsule_{day}.mp4"


def run_daily_wrapup(
    output_path: Path | None = None,
    day: str | None = None,
) -> str:

    day_dir = get_day_dir(day)

    if output_path is None:
        output_path = get_wrapup_output_path(day)

    print(f"⏱ Loading media from: {day_dir}")

    media = load_day_media(day_dir)

    if not media:
        print("No media found for this day.")
        return ""

    print(f"Found {len(media)} items")

    captions = caption_day_media(media)
    story = build_day_story(captions)

    script = build_trailer_script(
        media,
        title=story["title"],
        poem=story["poem"]
    )

    render_trailer(script, output_path)

    print("Wrap-up done ->", output_path)
    return str(output_path)
