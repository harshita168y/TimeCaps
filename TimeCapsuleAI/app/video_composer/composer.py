from __future__ import annotations

from pathlib import Path

import numpy as np
from moviepy.editor import (
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
    vfx,
)



from PIL import Image, ImageDraw, ImageFont

from app.story_engine.trailer_script import Shot, TrailerScript


VIDEO_SIZE = (1080, 1920)  # (width, height) for vertical video
FPS = 24


# ---------- Text rendering helpers (no ImageMagick needed) ----------

def _load_font(font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    Try to load a TTF font; fall back to default bitmap font if not found.
    """
    # Try common Windows font first
    for font_name in ["arial.ttf", "ARIAL.TTF"]:
        try:
            return ImageFont.truetype(font_name, font_size)
        except OSError:
            continue

    # Fallback: default PIL font
    return ImageFont.load_default()



def _make_text_image(
    text: str,
    size: tuple[int, int] = VIDEO_SIZE,
    font_size: int = 60,
    margin: int = 80,
    gradient: tuple[tuple[int, int, int], tuple[int, int, int]] | None = None,
) -> Image.Image:
    """
    Create an image with a vertical gradient background and centered multiline text.
    gradient: ((r1,g1,b1), (r2,g2,b2)) or None for solid black.
    """
    w, h = size

    # --- background: gradient or solid black ---
    if gradient is None:
        img = Image.new("RGB", size, (0, 0, 0))
    else:
        (r1, g1, b1), (r2, g2, b2) = gradient
        img = Image.new("RGB", size)
        draw_bg = ImageDraw.Draw(img)
        for y in range(h):
            t = y / max(h - 1, 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            draw_bg.line([(0, y), (w, y)], fill=(r, g, b))

    draw = ImageDraw.Draw(img)
    font = _load_font(font_size)

    words = text.split()
    lines: list[str] = []
    if not words:
        return img

    # ---------- word wrapping ----------
    current = words[0]
    for word in words[1:]:
        test_line = current + " " + word
        left, top, right, bottom = draw.textbbox((0, 0), test_line, font=font)
        line_width = right - left
        if line_width > w - 2 * margin:
            lines.append(current)
            current = word
        else:
            current = test_line
    lines.append(current)

    # ---------- total text height ----------
    line_heights = []
    for line in lines:
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bottom - top)

    total_text_height = sum(line_heights) + (len(lines) - 1) * 10
    y = (h - total_text_height) // 2

    # ---------- draw each line centered ----------
    for i, line in enumerate(lines):
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        line_width = right - left
        line_height = bottom - top
        x = (w - line_width) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += line_height + 10

    return img


# ---------- Clip constructors ----------

# def _title_card(shot: Shot):
#     text = shot.text or ""
#     img = _make_text_image(text, size=VIDEO_SIZE, font_size=72)
#     frame = np.array(img)
#     clip = ImageClip(frame).set_duration(shot.duration)
#     return clip.crossfadein(0.5)

# def _title_card(shot: Shot):
#     text = shot.text or ""
#     # e.g. deep blue -> purple
#     img = _make_text_image(
#         text,
#         size=VIDEO_SIZE,
#         font_size=72,
#         gradient=((10, 20, 80), (120, 0, 140)),
#     )
#     frame = np.array(img)
#     clip = ImageClip(frame).set_duration(shot.duration)
#     return clip.crossfadein(0.5)
def _video_shot(shot: Shot):
    clip = (
        VideoFileClip(str(shot.path))
        .subclip(0, shot.duration)
        # fill width
        .resize(width=VIDEO_SIZE[0])           # 1080 wide
        # pad to full 1080x1920
        .on_color(
            size=VIDEO_SIZE,
            color=(0, 0, 0),
            pos="center",
        )
    )
    return clip.crossfadein(0.2)
# def _image_shot(shot: Shot):
#     base = (
#         ImageClip(str(shot.path))
#         .resize(height=VIDEO_SIZE[1])
#         .set_duration(shot.duration)
#     )
#     return base.crossfadein(0.2)

def _image_shot(shot: Shot):
    base = (
        ImageClip(str(shot.path))
        # scale by width so we fill horizontally
        .resize(width=VIDEO_SIZE[0])           # 1080 wide, keep aspect ratio
        # pad to full 1080x1920 canvas
        .on_color(
            size=VIDEO_SIZE,
            color=(0, 0, 0),
            pos="center",
        )
        .set_duration(shot.duration)
    )
    return base.crossfadein(0.2)

def _video_shot(shot: Shot):
    clip = (
        VideoFileClip(str(shot.path))
        .subclip(0, shot.duration)
        .resize(height=VIDEO_SIZE[1])
    )
    return clip.crossfadein(0.2)


# def _poem_card(shot: Shot):
#     text = shot.text or ""
#     img = _make_text_image(text, size=VIDEO_SIZE, font_size=48)
#     frame = np.array(img)
#     clip = ImageClip(frame).set_duration(shot.duration)
#     return clip.crossfadein(0.5)

def _poem_card(shot: Shot):
    text = shot.text or ""
    # e.g. warm orange -> dark purple
    img = _make_text_image(
        text,
        size=VIDEO_SIZE,
        font_size=48,
        gradient=((160, 80, 0), (40, 0, 70)),
    )
    frame = np.array(img)
    clip = ImageClip(frame).set_duration(5)
    return clip.crossfadein(0.5)


# ---------- Main render function ----------

def render_trailer(script: TrailerScript, output_path: str | Path) -> None:
    clips = []

    for shot in script.shots:
        if shot.kind == "title_card":
            clips.append(_poem_card(shot))
        elif shot.kind == "image":
            clips.append(_image_shot(shot))
        elif shot.kind == "video_clip":
            clips.append(_video_shot(shot))
        elif shot.kind == "poem_card":
            clips.append(_poem_card(shot))

    final = concatenate_videoclips(clips, method="compose")

    # final = final.resize(VIDEO_SIZE)

    # 🔹 Make sure width & height are EVEN (many decoders require this)
    w, h = final.size
    even_w = w - (w % 2)
    even_h = h - (h % 2)
    if even_w != w or even_h != h:
      print(f"[VIDEO] Adjusting size from {w}x{h} to {even_w}x{even_h} for compatibility.")
      final = final.resize((even_w, even_h))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    final.write_videofile(
        str(output_path),
        fps=24,                 # lower fps -> fewer frames to encode
        codec="libx264",
        audio_codec="aac",
        preset="superfast",     # faster encoding (bigger file but fine for dev)
        bitrate="2000k",   
        ffmpeg_params=[
        "-profile:v", "baseline",  # simpler profile
        "-level", "3.0",           # low-ish level
        "-pix_fmt", "yuv420p",     # widely supported pixel format
    ],
    )
