from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from app.media_processing.loader import MediaItem
ShotKind = Literal["title_card", "image", "video_clip", "poem_card"]
@dataclass
class Shot:
    kind: ShotKind
    path: Path | None
    duration: float
    text: str | None = None
@dataclass
class TrailerScript:
    shots: list[Shot]
    @property
    def total_duration(self) -> float:
        return sum(s.duration for s in self.shots)
def build_trailer_script(
    media: list[MediaItem],
    title: str,
    poem: str,
    image_duration: float = 1.0,
    max_video_segment: float = 4.0,
) -> TrailerScript:
    """
    Simple linear structure:
    1. Title card
    2. Image montage
    3. Short slices from each video
    4. Poem card
    """
    shots: list[Shot] = []
    # 1. Title card
    shots.append(
        Shot(
            kind="title_card",
            path=None,
            duration=3.0,
            text=title,
        )
    )
    # 2. Images
    for m in media:
        if m.media_type == "image":
            shots.append(
                Shot(
                    kind="image",
                    path=m.path,
                    duration=image_duration,
                )
            )
    # 3. Videos
    for m in media:
        if m.media_type == "video" and (m.duration or 0) > 0:
            dur = min(max_video_segment, m.duration)
            shots.append(
                Shot(
                    kind="video_clip",
                    path=m.path,
                    duration=dur,
                )
            )
    # 4. Poem card
    poem_lines = poem.strip()
    poem_duration = max(7.0, len(poem_lines.splitlines()) * 1.2)
    shots.append(
        Shot(
            kind="poem_card",
            path=None,
            duration=poem_duration,
            text=poem_lines,
        )
    )
    return TrailerScript(shots=shots)
