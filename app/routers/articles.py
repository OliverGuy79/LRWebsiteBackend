"""Articles API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.models.articles import ArticleBase, ArticleFull, ArticleListResponse
from app.services import sheets_service, docs_service


router = APIRouter()


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    status: str | None = Query(None, description="Filter by status (e.g., 'published')"),
    category: str | None = Query(None, description="Filter by category"),
    limit: int | None = Query(None, description="Limit number of results"),
):
    """
    List all articles (metadata only, no content).
    
    Use the single article endpoint to get full content.
    """
    data = await sheets_service.get_articles()
    
    # Filter by status if provided
    if status:
        data = [a for a in data if a.get("status", "").lower() == status.lower()]
    
    # Filter by category if provided
    if category:
        data = [a for a in data if a.get("category", "").lower() == category.lower()]
    
    # Sort by published_at (newest first)
    data.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    
    # Limit results if specified
    if limit:
        data = data[:limit]
    
    articles = [ArticleBase(**article) for article in data]
    return ArticleListResponse(articles=articles, total=len(articles))


@router.get("/{slug}", response_model=ArticleFull)
async def get_article(slug: str):
    """
    Get a single article by slug, including full HTML content from Google Doc.
    """
    data = await sheets_service.get_articles()
    
    # Find article by slug
    article_data = next((a for a in data if a.get("slug") == slug), None)
    
    if not article_data:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Fetch content from Google Doc - use 'link' column for doc URL
    doc_url = article_data.get("link") or article_data.get("content")
    content_html = await docs_service.get_article_content(doc_url)
    
    return ArticleFull(
        **article_data,
        content_html=content_html
    )
