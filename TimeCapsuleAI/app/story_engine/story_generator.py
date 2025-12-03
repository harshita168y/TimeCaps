from __future__ import annotations

from app.media_processing.object_tags import extract_keywords_from_captions
from app.story_engine.wrapup_llm import generate_poem_from_captions


def build_day_story(captions: list[str]) -> dict:
    """
    Basic story object; extend later with title, sections, etc.
    """
    poem = generate_poem_from_captions(captions)
    keywords = extract_keywords_from_captions(captions)
    title = "A Day of " + (", ".join(word.capitalize() for word in keywords[:3]) or "Moments")
    return {
        "title": title,
        "poem": poem,
        "keywords": keywords,
    }
