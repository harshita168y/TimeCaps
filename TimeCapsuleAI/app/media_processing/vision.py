from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Iterable
import cv2
import google.generativeai as genai
from app.media_processing.loader import MediaItem, grab_video_frame
from app.utils.helpers import get_env
import json
from pathlib import Path
_IMAGE_MODEL = None  # lazy init
CAPTION_CACHE_PATH = Path("caption_cache.json")

def _load_caption_cache() -> dict:
    if CAPTION_CACHE_PATH.exists():
        try:
            return json.loads(CAPTION_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[CAPTION CACHE] Failed to read cache: {e}")
            return {}
    return {}

def _save_caption_cache(cache: dict) -> None:
    try:
        CAPTION_CACHE_PATH.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[CAPTION CACHE] Saved {len(cache)} entries.")
    except Exception as e:
        print(f"[CAPTION CACHE] Failed to save cache: {e}")

def _get_image_model():
    """
    Returns a Gemini multimodal model that works with YOUR account.

    Using 'gemini-2.5-flash' from your list_models().
    """
    global _IMAGE_MODEL
    if _IMAGE_MODEL is None:
        api_key = get_env("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        _IMAGE_MODEL = genai.GenerativeModel("gemini-2.5-flash")
    return _IMAGE_MODEL

def _bgr_to_jpeg_bytes(frame) -> bytes:
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        raise RuntimeError("Failed to encode frame as JPG")
    return buf.tobytes()


def _format_time(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.strftime("%H:%M")  

def _time_of_day(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    hour = dt.hour
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"

def _wrap_caption_with_context(
    base_caption: str,
    taken_at: datetime | None,
    location: str | None,
) -> str:
    """
    Build a richer caption used for the poem:
    e.g. "07:34 in the morning at 53.34, -6.26: a warm mug of coffee..."
    """
    pieces = []
    t_str = _format_time(taken_at)
    tod = _time_of_day(taken_at)
    if t_str:
        if tod:
            pieces.append(f"{t_str} in the {tod}")
        else:
            pieces.append(t_str)

    if location:
        pieces.append(f"at {location}")

    if pieces:
        return f"{' '.join(pieces)}: {base_caption}"
    else:
        return base_caption
    
def describe_image_path(path: Path) -> str:
    model = _get_image_model()
    img_bytes = path.read_bytes()
    prompt = (
        "Describe this photo in one short, vivid sentence. "
        "Focus on the key subject and mood. No camera jargon."
    )
    print(f"\n[VISION] Calling {model.model_name} for image:")
    print(f"        path = {path}")
    print(f"        prompt = {prompt}")

    resp = model.generate_content(
        [prompt, {"mime_type": "image/jpeg", "data": img_bytes}]
    )
    return (resp.text or "").strip()

def describe_frame(frame) -> str:
    model = _get_image_model()
    img_bytes = _bgr_to_jpeg_bytes(frame)
    prompt = (
        "Describe this moment from a video in one short sentence. "
        "Focus on what's happening and the feeling."
    )

    print(f"\n[VISION] Calling {model.model_name} for video frame")
    print(f"        prompt = {prompt}")

    resp = model.generate_content(
        [prompt, {"mime_type": "image/jpeg", "data": img_bytes}]
    )
    return (resp.text or "").strip()
def caption_day_media(media):
    """
    Returns a list of captions for the given media items.
    - Images: use Gemini via describe_image_path (with cache)
    - Videos: use a simple fallback caption (no Gemini)
    """
    cache = _load_caption_cache()
    updated = False
    captions = []
    for item in media:
        key = str(Path(item.path).resolve())

        if key in cache:
            caption = cache[key]
            print(f"📝 Using cached caption for {item.path}")
        else:
            media_type = getattr(item, "media_type", "")
            filename = Path(item.path).name

            if media_type == "image":
                print(f"🆕 Captioning IMAGE {item.path} with Gemini...")
                caption = describe_image_path(item.path)
                print(f"   → {caption[:80]}...")
            else:
                print(f"🎥 Skipping Gemini for VIDEO {item.path}, using simple caption.")
                caption = f"Short video clip from {filename}"

            cache[key] = caption
            updated = True

        captions.append(caption)
    if updated:
        _save_caption_cache(cache)
    return captions
 