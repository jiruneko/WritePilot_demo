# app/config.py
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()  # .env を読む

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Put it in .env")
