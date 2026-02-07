"""Service for fetching content from public Google Docs."""

import re

import httpx

from app.config import get_settings
from app.services.cache_service import get_cache


settings = get_settings()
cache = get_cache(settings.cache_ttl_seconds)


async def fetch_doc_html(doc_url: str, use_cache: bool = True) -> str | None:
    """
    Fetch HTML content from a public Google Doc.
    
    Args:
        doc_url: The Google Doc URL (edit or view link)
        use_cache: Whether to use cached data if available
        
    Returns:
        HTML content of the document, or None if fetch fails
    """
    # Extract doc ID from URL
    doc_id = settings.extract_doc_id(doc_url)
    if not doc_id:
        return None
    
    cache_key = f"doc:{doc_id}"
    
    # Check cache first
    if use_cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    
    # Fetch HTML from Google Docs
    export_url = settings.get_doc_html_url(doc_id)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(export_url, follow_redirects=True)
            response.raise_for_status()
            
        html_content = response.text
        
        # Clean up the HTML - extract body content and clean Google's styling
        html_content = clean_google_doc_html(html_content)
        
        # Cache the result
        cache.set(cache_key, html_content)
        
        return html_content
        
    except httpx.HTTPError:
        return None


def clean_google_doc_html(html: str) -> str:
    """
    Clean up Google Docs exported HTML.
    
    Removes Google's wrapper elements and simplifies the HTML
    while preserving the article formatting.
    """
    # Extract body content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
    if body_match:
        html = body_match.group(1)
    
    # Remove Google's comment elements
    html = re.sub(r'<a[^>]*id="cmnt[^"]*"[^>]*>.*?</a>', '', html, flags=re.DOTALL)
    
    # Remove script tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Keep the HTML but it may still have Google's classes
    # The frontend can handle styling or you can add more cleanup here
    
    return html.strip()


async def get_article_content(doc_url: str | None, use_cache: bool = True) -> str | None:
    """
    Get article content from a Google Doc URL.
    
    This is a convenience wrapper that handles None URLs gracefully.
    """
    if not doc_url:
        return None
    return await fetch_doc_html(doc_url, use_cache=use_cache)
