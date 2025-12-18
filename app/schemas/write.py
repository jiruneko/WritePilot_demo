# app/schemas/write.py
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    audience: str = Field(default="general", max_length=50)
    tone: str = Field(default="friendly", max_length=50)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "How to build a fast API with FastAPI",
                    "audience": "developers",
                    "tone": "confident",
                }
            ]
        }
    }

class GenerateResponse(BaseModel):
    id: int
    title: str
    article: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "How to build a fast API with FastAPI",
                    "article": (
                        "# How to Build a Fast API with FastAPI\n\n"
                        "FastAPI is a modern, high-performance web framework for building APIs with Python.\n\n"
                        "## Why FastAPI?\n"
                        "- Extremely fast\n"
                        "- Easy to use\n"
                        "- Automatic API documentation\n\n"
                        "Start building faster APIs today."
                    ),
                }
            ]
        }
    }

from datetime import datetime

class ArticleOut(BaseModel):
    id: int
    title: str
    audience: str
    tone: str
    article: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "FastAPI Tips",
                    "audience": "developers",
                    "tone": "confident",
                    "article": "This article was manually edited.",
                    "created_at": "2025-12-18T12:59:29.124631",
                    "updated_at": "2025-12-18T12:59:45.250751",
                }
            ]
        }
    }

class RewriteRequest(BaseModel):
    tone: str = Field(default="friendly", max_length=50)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"tone": "casual"},
                {"tone": "professional"},
                {"tone": "confident"},
            ]
        }
    }

class ArticleUpdate(BaseModel):
    title: str | None = None
    audience: str | None = None
    tone: str | None = None
    article: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"title": "Updated title only"},
                {"tone": "casual"},
                {"article": "This article was manually edited."},
                {
                    "title": "Polished FastAPI Tips",
                    "audience": "developers",
                    "tone": "friendly",
                    "article": "Full replacement / bulk edit example.",
                },
            ]
        }
    }