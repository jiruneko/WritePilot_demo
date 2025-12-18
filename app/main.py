# app/main.py
from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.write import router as write_router
from app.db.database import Base, engine
from app.db import models  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(
        title="WritePilot Demo API",
        version="0.2.0",
        summary="AI-powered English CMS backend demo",
        description=(
            "WritePilot is a minimal demo backend for an AI-powered English CMS.\n\n"
            "Features:\n"
            "- Generate English blog articles with OpenAI\n"
            "- Persist articles to SQLite\n"
            "- Full CRUD: create, list, get, update (PUT/PATCH), delete\n\n"
            "Use cases:\n"
            "- Portfolio demo\n"
            "- MVP validation\n"
            "- Upwork / overseas client showcase"
        ),
        contact={
            "name": "WritePilot (Demo)",
        },
        license_info={
            "name": "MIT",
        },
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS（必要なオリジンだけに絞るのが理想。デモはこれでOK）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(write_router, prefix="/api")

    @app.get(
        "/",
        tags=["health"],
        summary="Health check",
        description="Returns basic service status.",
    )
    def root():
        return {"status": "ok", "service": "writepilot-demo"}

    return app


# DB init (demo)
Base.metadata.create_all(bind=engine)

app = create_app()
from app.ui.web import router as ui_router
app.include_router(ui_router)
