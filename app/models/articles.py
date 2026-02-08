"""Pydantic models for Articles."""

from pydantic import BaseModel, Field


class ArticleBase(BaseModel):
    """Article metadata (without full content)."""
    id: str
    title: str
    slug: str
    content: str | None = None  # Content from sheet (not used if using Google Docs)
    excerpt: str | None = None
    author: str | None = None
    category: str | None = None
    tags: str | None = None
    image: str | None = None  # was featured_image
    media: str | None = None  # link to attached media
    status: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    published_at: str | None = None
    link: str | None = None  # Google Doc link for content


class ArticleFull(ArticleBase):
    """Full article with HTML content from Google Doc."""
    content_html: str | None = None


class ArticleListResponse(BaseModel):
    """Response for listing articles."""
    articles: list[ArticleBase]
    total: int
