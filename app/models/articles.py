"""Pydantic models for Articles."""

from pydantic import BaseModel
from datetime import datetime


class ArticleBase(BaseModel):
    """Article metadata (without full content)."""
    id: str
    title: str
    slug: str
    excerpt: str | None = None
    author: str | None = None
    category: str | None = None
    tags: str | None = None
    feature_image: str | None = None
    status: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    published_at: str | None = None


class ArticleFull(ArticleBase):
    """Full article with HTML content from Google Doc."""
    content_html: str | None = None


class ArticleListResponse(BaseModel):
    """Response for listing articles."""
    articles: list[ArticleBase]
    total: int
