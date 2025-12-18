# app/ui/web.py
from __future__ import annotations

import traceback

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Article
from app.services.openai_client import generate_article, rewrite_article

router = APIRouter(prefix="/ui", tags=["ui"])
templates = Jinja2Templates(directory="app/templates")


# ----------------------------
# Helpers
# ----------------------------
def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


def _get_article_or_404(db: Session, article_id: int) -> Article:
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    return a


def _is_blank(text: str | None) -> bool:
    return text is None or not str(text).strip()


def _log_exc(prefix: str, exc: Exception) -> None:
    # UIではJSONで詳細を返さない。その代わりサーバ側にだけ出す。
    print(f"{prefix}: {repr(exc)}")
    traceback.print_exc()


# ----------------------------
# Pages
# ----------------------------
@router.get("/", response_class=HTMLResponse, summary="UI: index")
def ui_index(request: Request, db: Session = Depends(get_db)):
    stmt = select(Article).order_by(Article.id.desc())
    articles = db.execute(stmt).scalars().all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "articles": articles},
    )


@router.get("/new", response_class=HTMLResponse, summary="UI: new article")
def ui_new(request: Request, error: str | None = None):
    return templates.TemplateResponse(
        "new.html",
        {"request": request, "error": error},
    )


@router.get(
    "/articles/{article_id}",
    response_class=HTMLResponse,
    summary="UI: edit article",
)
def ui_edit(
    article_id: int,
    request: Request,
    db: Session = Depends(get_db),
    error: str | None = None,
):
    a = _get_article_or_404(db, article_id)
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "a": a, "error": error},
    )


# ----------------------------
# Actions
# ----------------------------
@router.post("/generate", summary="UI: generate & save")
def ui_generate(
    title: str = Form(...),
    audience: str = Form("general"),
    tone: str = Form("friendly"),
    db: Session = Depends(get_db),
):
    try:
        # generate_article 側で「空なら例外」に統一しておく想定
        article_text = generate_article(title, audience, tone)
    except Exception as e:
        _log_exc("LLM generate failed", e)
        return _redirect("/ui/new?error=llm_failed")

    if _is_blank(article_text):
        # 万一、generate_article が空を返した場合の保険
        _log_exc("LLM generate failed", ValueError("LLM returned empty content"))
        return _redirect("/ui/new?error=llm_failed")

    row = Article(
        title=title,
        audience=audience,
        tone=tone,
        content=article_text,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return _redirect(f"/ui/articles/{row.id}")


@router.post("/articles/{article_id}/update", summary="UI: update article")
def ui_update(
    article_id: int,
    title: str = Form(...),
    audience: str = Form(...),
    tone: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    if _is_blank(content):
        return _redirect(f"/ui/articles/{article_id}?error=empty_content")

    a = _get_article_or_404(db, article_id)
    a.title = title
    a.audience = audience
    a.tone = tone
    a.content = content

    db.commit()
    db.refresh(a)

    return _redirect(f"/ui/articles/{a.id}")


@router.post("/articles/{article_id}/rewrite", summary="UI: rewrite article")
def ui_rewrite(
    article_id: int,
    tone: str = Form("friendly"),
    db: Session = Depends(get_db),
):
    a = _get_article_or_404(db, article_id)

    try:
        # rewrite_article 側で「空なら例外」に統一しておく想定
        rewritten = rewrite_article(a.content, tone)
    except Exception as e:
        _log_exc("LLM rewrite failed", e)
        return _redirect(f"/ui/articles/{article_id}?error=llm_failed")

    if _is_blank(rewritten):
        # 万一、rewrite_article が空を返した場合の保険
        _log_exc("LLM rewrite failed", ValueError("LLM returned empty content"))
        return _redirect(f"/ui/articles/{article_id}?error=llm_failed")

    a.content = rewritten
    a.tone = tone

    db.commit()
    db.refresh(a)

    return _redirect(f"/ui/articles/{a.id}")


@router.post("/articles/{article_id}/delete", summary="UI: delete article")
def ui_delete(article_id: int, db: Session = Depends(get_db)):
    a = _get_article_or_404(db, article_id)
    db.delete(a)
    db.commit()
    return _redirect("/ui")
