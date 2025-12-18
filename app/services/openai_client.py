# app/services/openai_client.py
from __future__ import annotations

import os

from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client = OpenAI(api_key=OPENAI_API_KEY)


def _require_non_empty(text: str | None, msg: str) -> str:
    if text is None or not str(text).strip():
        raise RuntimeError(msg)
    return str(text).strip()


def generate_article(title: str, audience: str = "general", tone: str = "friendly") -> str:
    prompt = f"""
You are WritePilot, an AI writing assistant for English blogs.

Write an English blog article.

Requirements:
- Title: {title}
- Audience: {audience}
- Tone: {tone}
- Use Markdown
- Add headings (##) and bullet points where helpful
- End with a short conclusion

Output only the article in Markdown.
""".strip()

    res = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful writing assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    choice = res.choices[0]
    content = (choice.message.content or "").strip()

    return _require_non_empty(
        content,
        f"Empty LLM content (finish_reason={getattr(choice, 'finish_reason', None)}, "
        f"has_tool_calls={bool(getattr(choice.message, 'tool_calls', None))})",
    )


def rewrite_article(text: str, target_tone: str = "friendly") -> str:
    prompt = f"""
You are WritePilot, an AI writing assistant for English blogs.

Rewrite the following article in English.

Requirements:
- Keep the meaning
- Improve clarity and flow
- Tone: {target_tone}
- Keep headings (##) if present
- Output only the rewritten article in Markdown

ARTICLE:
{text}
""".strip()

    res = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful writing assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    choice = res.choices[0]
    content = (choice.message.content or "").strip()

    return _require_non_empty(
        content,
        f"Empty LLM content (finish_reason={getattr(choice, 'finish_reason', None)}, "
        f"has_tool_calls={bool(getattr(choice.message, 'tool_calls', None))})",
    )
