from __future__ import annotations

from textwrap import dedent

import google.generativeai as genai

from app.utils.helpers import get_env

_TEXT_MODEL = None


def _get_text_model():
    """
    Returns a text/multimodal model that works with YOUR account.

    We reuse 'gemini-2.5-flash' for text-only generation.
    """
    global _TEXT_MODEL
    if _TEXT_MODEL is None:
        api_key = get_env("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        # 👇 also from your list_models() output
        _TEXT_MODEL = genai.GenerativeModel("gemini-2.5-flash")
    return _TEXT_MODEL


def generate_poem_from_captions(captions: list[str]) -> str:
    """Turn a list of visual captions into a short wrap-up poem."""
    model = _get_text_model()
    limited = captions[:60]  # safety limit
    joined = "\n".join(f"- {c}" for c in limited)

    prompt = dedent(
        f"""
        You're writing the closing voice-over poem for a cinematic 'day in the life'
        trailer. The lines below are descriptions of photos and video moments
        from the person's day:

        {joined}

        Write a warm, slightly cinematic free-verse poem of 3-4 short lines.
        Rules:
        - Do NOT mention 'photos', 'videos', 'camera', or 'captions'
        - Talk as if you watched the day unfold directly
        - Focus on feelings, small details, and transitions from morning to night
        - Keep language simple and human, not overly flowery or cheesy.
        """
    ).strip()

    # 👇 DEBUG LOG
    print("\n[POEM] Calling", model.model_name)
    print("[POEM] Prompt being sent to Gemini:\n")
    print(prompt)
    print("\n[POEM] --------------------\n")
    resp = model.generate_content(prompt)
    return (resp.text or "").strip()
