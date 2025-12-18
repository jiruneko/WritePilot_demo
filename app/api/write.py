# app/api/write.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Article
from app.schemas.write import (
    ArticleOut,
    ArticleUpdate,
    GenerateRequest,
    GenerateResponse,
    RewriteRequest,
)
from app.services.openai_client import generate_article, rewrite_article

router = APIRouter(tags=["write"])


# ----------------------------
# Helpers
# ----------------------------
def _to_article_out(a: Article) -> ArticleOut:
    return ArticleOut(
        id=a.id,
        title=a.title,
        audience=a.audience,
        tone=a.tone,
        article=a.content,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


def _get_article_or_404(db: Session, article_id: int) -> Article:
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    return a


def _apply_update(a: Article, req: ArticleUpdate) -> None:
    if req.title is not None:
        a.title = req.title
    if req.audience is not None:
        a.audience = req.audience
    if req.tone is not None:
        a.tone = req.tone
    if req.article is not None:
        a.content = req.article


def _require_non_empty(text: str | None, message: str) -> str:
    if text is None or not str(text).strip():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=message,
        )
    return text


# ----------------------------
# Routes
# ----------------------------
@router.get(
    "/ping",
    summary="Ping",
    description="Simple liveness check for the write router.",
)
def ping():
    return {"message": "write api alive"}


@router.post(
    "/generate",
    response_model=GenerateResponse,
    summary="Generate an article",
    description="Generates an English blog article using OpenAI and saves it to the database.",
)
def generate(req: GenerateRequest, db: Session = Depends(get_db)):
    try:
        article_text = generate_article(req.title, req.audience, req.tone)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM generation failed: {e}",
        )

    article_text = _require_non_empty(article_text, "LLM generation returned empty content")

    row = Article(
        title=req.title,
        audience=req.audience,
        tone=req.tone,
        content=article_text,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return GenerateResponse(
        id=row.id,
        title=row.title,
        article=row.content,
    )


@router.get(
    "/articles",
    response_model=list[ArticleOut],
    summary="List articles",
    description="Returns all articles ordered by newest first.",
)
def list_articles(db: Session = Depends(get_db)):
    stmt = select(Article).order_by(Article.id.desc())
    rows = db.execute(stmt).scalars().all()
    return [_to_article_out(a) for a in rows]


@router.get(
    "/articles/{article_id}",
    response_model=ArticleOut,
    summary="Get an article",
    description="Fetch a single article by ID.",
)
def get_article(article_id: int, db: Session = Depends(get_db)):
    a = _get_article_or_404(db, article_id)
    return _to_article_out(a)


@router.put(
    "/articles/{article_id}",
    response_model=ArticleOut,
    summary="Update an article",
    description="Updates an article. (Demo behavior: updates only provided fields.)",
)
def update_article(article_id: int, req: ArticleUpdate, db: Session = Depends(get_db)):
    a = _get_article_or_404(db, article_id)

    _apply_update(a, req)
    if a.content is None or not str(a.content).strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Article content cannot be empty",
        )

    db.commit()
    db.refresh(a)
    return _to_article_out(a)


@router.patch(
    "/articles/{article_id}",
    response_model=ArticleOut,
    summary="Patch an article",
    description="Partially updates an article (only provided fields are updated).",
)
def patch_article(article_id: int, req: ArticleUpdate, db: Session = Depends(get_db)):
    a = _get_article_or_404(db, article_id)

    _apply_update(a, req)
    if a.content is None or not str(a.content).strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Article content cannot be empty",
        )

    db.commit()
    db.refresh(a)
    return _to_article_out(a)


@router.delete(
    "/articles/{article_id}",
    summary="Delete an article",
    description="Deletes an article by ID.",
)
def delete_article(article_id: int, db: Session = Depends(get_db)):
    a = _get_article_or_404(db, article_id)

    db.delete(a)
    db.commit()
    return {"deleted": True, "id": article_id}


@router.post(
    "/rewrite/{article_id}",
    response_model=ArticleOut,
    summary="Rewrite an article",
    description="Rewrites an existing article with a new tone using OpenAI, then saves it.",
)
def rewrite(article_id: int, req: RewriteRequest, db: Session = Depends(get_db)):
    a = _get_article_or_404(db, article_id)

    try:
        rewritten = rewrite_article(a.content, req.tone)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM rewrite failed: {e}",
        )

    rewritten = _require_non_empty(rewritten, "LLM rewrite returned empty content")

    a.content = rewritten
    a.tone = req.tone

    db.commit()
    db.refresh(a)
    return _to_article_out(a)
