# from datetime import datetime
# from typing import Dict, List

# from app.media_processing.vision import classify_media_scene
# from app.media_processing.object_tags import extract_objects_from_image
# from moviepy.editor import VideoFileClip
# from PIL import Image
# from pathlib import Path



# def unix_to_datetime(timestamp: float) -> datetime:
#     """Convert a Unix timestamp to a Python datetime object."""
#     return datetime.fromtimestamp(timestamp)


# def get_part_of_day(dt: datetime) -> str:
#     """
#     Roughly classify the part of day based on hour.
#     Morning:   5  - 11
#     Afternoon: 12 - 16
#     Evening:   17 - 21
#     Night:     22 - 4
#     """
#     hour = dt.hour

#     if 5 <= hour <= 11:
#         return "Morning"
#     elif 12 <= hour <= 16:
#         return "Afternoon"
#     elif 17 <= hour <= 21:
#         return "Evening"
#     else:
#         return "Night"


# def build_timeline(media_files: List[Dict]) -> List[Dict]:
#     """
#     Take the raw media file metadata and enrich it with:
#     - datetime object
#     - human-readable time string
#     - part_of_day label

#     Returns a new list of entries like:
#     {
#         "path": ...,
#         "name": ...,
#         "extension": ...,
#         "modified_time": ...,
#         "datetime": datetime(...),
#         "time_str": "08:42",
#         "part_of_day": "Morning"
#     }
#     """
#     timeline = []

#     for item in media_files:
#         dt = unix_to_datetime(item["modified_time"])
#         part = get_part_of_day(dt)

#         enriched = {
#             **item,
#             "datetime": dt,
#             "time_str": dt.strftime("%H:%M"),
#             "part_of_day": part,
#         }
#         timeline.append(enriched)

#     # They should already be sorted by modified_time,
#     # but we can enforce it just in case:
#     timeline.sort(key=lambda x: x["datetime"])

#     return timeline

# def enrich_timeline_with_scenes(timeline):
#     """
#     Take the raw timeline items and add:
#       - 'scene': a simple high-level label
#       - 'objects': empty list for now (no extra CV model)
#     This keeps the rest of the pipeline working without extra dependencies.
#     """
#     enriched = []

#     for item in timeline:
#         path = item["path"].lower()
#         ext = item["extension"].lower()

#         # Very simple heuristic scene labels based on extension/name
#         scene = "Unknown"
#         if ext in {".jpg", ".jpeg", ".png"}:
#             if "food" in path or "lunch" in path or "dinner" in path:
#                 scene = "Food / Meal"
#             elif "selfie" in path or "portrait" in path:
#                 scene = "Self / People"
#             elif "out" in path or "park" in path or "beach" in path:
#                 scene = "Outdoors"
#             else:
#                 scene = "Photo"
#         elif ext in {".mp4", ".mov", ".avi", ".mkv"}:
#             scene = "Video Moment"

#         item["scene"] = scene
#         item["objects"] = []  # no object detection for now

#         enriched.append(item)

#     return enriched



from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


_ENV_LOADED = False


def load_env() -> None:
    """Load environment variables from .env exactly once."""
    global _ENV_LOADED
    if not _ENV_LOADED:
        load_dotenv()
        _ENV_LOADED = True


def get_env(key: str) -> str:
    load_env()
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing environment variable: {key}")
    return value


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def list_media_files(root: str | Path) -> list[Path]:
    """Return all image/video files under root, sorted by modification time."""
    root = Path(root)
    exts = {".jpg", ".jpeg", ".png", ".mp4", ".mov", ".mkv"}
    files = [p for p in root.glob("**/*") if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime)
    return files
