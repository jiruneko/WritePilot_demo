from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.write import router as write_router
from app.ui.web import router as ui_router
from app.db.database import Base, engine
from app.db import models  # noqa: F401


# -------------------------------------------------
# App factory
# -------------------------------------------------
def create_app() -> FastAPI:
    # Load environment variables (.env for local, Render uses ENV vars)
    load_dotenv()

    app = FastAPI(
        title="WritePilot Demo API",
        version="0.2.0",
        summary="AI-powered English CMS demo",
        description=(
            "WritePilot is a minimal demo application for an AI-powered English CMS.\n\n"
            "Features:\n"
            "- Generate English blog articles with OpenAI\n"
            "- Rewrite articles by tone\n"
            "- Persist articles to SQLite\n"
            "- Full CRUD via REST API and Web UI\n\n"
            "Use cases:\n"
            "- Portfolio demo\n"
            "- MVP validation\n"
            "- Overseas / Upwork client showcase"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # -------------------------------------------------
    # Middleware
    # -------------------------------------------------
    # Demo-friendly CORS (tighten for production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------
    # Routes
    # -------------------------------------------------
    # Root: redirect to UI
    @app.get(
        "/",
        tags=["ui"],
        summary="Redirect to UI",
        description="Redirects the root path to the Web UI.",
    )
    def root() -> RedirectResponse:
        return RedirectResponse(url="/ui")

    # API & UI routers
    app.include_router(write_router, prefix="/api")
    app.include_router(ui_router)

    return app


# -------------------------------------------------
# DB init (demo purpose)
# -------------------------------------------------
Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# ASGI app
# -------------------------------------------------
app = create_app()
