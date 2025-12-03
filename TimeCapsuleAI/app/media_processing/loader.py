from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
from PIL import Image, ExifTags
from app.utils.helpers import list_media_files
MediaType = Literal["image", "video"]
@dataclass
class MediaItem:
    path: Path
    media_type: MediaType
    duration: float | None 
    taken_at: Optional[datetime] = None
    location: Optional[str] = None 
def _get_video_duration(path: Path) -> float:
    with VideoFileClip(str(path)) as clip:
        return float(clip.duration)
_EXIF_TAGS = {v: k for k, v in ExifTags.TAGS.items()}
def _parse_exif_datetime(raw: str) -> Optional[datetime]:
    try:
        return datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None
def _convert_gps_coord(value, ref) -> float:
    """
    Convert EXIF GPS coord to decimal degrees.
    value is ((deg_num, deg_den), (min_num, min_den), (sec_num, sec_den))
    """
    try:
        d = value[0][0] / value[0][1]
        m = value[1][0] / value[1][1]
        s = value[2][0] / value[2][1]
        coord = d + (m / 60.0) + (s / 3600.0)
        if ref in ["S", "W"]:
            coord = -coord
        return coord
    except Exception:
        return 0.0
def _extract_image_metadata(path: Path) -> tuple[Optional[datetime], Optional[str]]:
    """
    Read EXIF for capture time + GPS location.
    Returns (taken_at, location_str)
    """
    taken_at: Optional[datetime] = None
    location: Optional[str] = None

    try:
        img = Image.open(str(path))
        exif = img._getexif()
        if not exif:
            return taken_at, location
        dt_tag = _EXIF_TAGS.get("DateTimeOriginal") or _EXIF_TAGS.get("DateTime")
        if dt_tag and dt_tag in exif:
            raw_dt = exif[dt_tag]
            taken_at = _parse_exif_datetime(raw_dt)
        gps_tag = _EXIF_TAGS.get("GPSInfo")
        if gps_tag and gps_tag in exif:
            gps_info = exif[gps_tag]
            gps_data = {}
            for t in gps_info:
                gps_data[ExifTags.GPSTAGS.get(t, t)] = gps_info[t]

            lat = lon = None
            if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
                lat = _convert_gps_coord(gps_data["GPSLatitude"], gps_data["GPSLatitudeRef"])
            if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
                lon = _convert_gps_coord(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])

            if lat is not None and lon is not None:
                location = f"{lat:.4f}, {lon:.4f}"

    except Exception:
        pass

    return taken_at, location
def load_day_media(root: str | Path) -> list[MediaItem]:
    """
    Scan directory and return media items sorted by capture time if available,
    otherwise by file modification time.
    """
    media_items: list[MediaItem] = []
    for p in list_media_files(root):
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            taken_at, location = _extract_image_metadata(p)
            # fallback: file modification time if no EXIF date
            if taken_at is None:
                taken_at = datetime.fromtimestamp(p.stat().st_mtime)

            media_items.append(
                MediaItem(
                    path=p,
                    media_type="image",
                    duration=None,
                    taken_at=taken_at,
                    location=location,
                )
            )
        else:
            duration = _get_video_duration(p)
            taken_at = datetime.fromtimestamp(p.stat().st_mtime)
            media_items.append(
                MediaItem(
                    path=p,
                    media_type="video",
                    duration=duration,
                    taken_at=taken_at,
                    location=None, 
                )
            )
    media_items.sort(key=lambda m: m.taken_at or datetime.fromtimestamp(m.path.stat().st_mtime))
    return media_items
def grab_video_frame(path: Path, time_s: float) -> np.ndarray:
    """Grab a BGR frame at `time_s` seconds in the video."""
    cap = cv2.VideoCapture(str(path))
    cap.set(cv2.CAP_PROP_POS_MSEC, time_s * 1000)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError(f"Could not read frame from {path} at {time_s:.2f}s")
    return frame
