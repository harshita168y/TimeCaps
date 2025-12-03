from __future__ import annotations
from collections import Counter
from typing import Iterable
def extract_keywords_from_captions(
    captions: Iterable[str],
    max_keywords: int = 10,
) -> list[str]:
    """
    Very simple keyword extractor: split words, count frequency, filter small
    filler words. Used to create a short 'vibe' title for the day.
    """
    stop = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "of",
        "in",
        "on",
        "at",
        "with",
        "to",
        "from",
        "for",
        "is",
        "are",
        "this",
        "that",
        "it",
        "its",
        "into",
        "by",
        "as",
        "over",
        "under",
        "up",
        "down",
        "near",
        "around",
        "between",
        "during",
        "my",
        "our",
        "your",
        "their",
        "his",
        "her",
        "them",
        "you",
        "we",
        "i",
    }
    counts: Counter[str] = Counter()
    for caption in captions:
        words = (
            caption.lower()
            .replace(",", " ")
            .replace(".", " ")
            .replace("!", " ")
            .replace("?", " ")
            .split()
        )
        for w in words:
            w = "".join(ch for ch in w if ch.isalpha())
            if not w or w in stop or len(w) <= 2:
                continue
            counts[w] += 1
    return [word for word, _ in counts.most_common(max_keywords)]
