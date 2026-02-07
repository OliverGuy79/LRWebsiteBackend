"""Service for fetching data from public Google Sheets."""

import csv
import io
from typing import Any
import logging
import httpx

from app.config import get_settings
from app.services.cache_service import get_cache


settings = get_settings()
cache = get_cache(settings.cache_ttl_seconds)


async def fetch_sheet_data(
    sheet_id: str,
    tab_name: str | None = None,
    use_cache: bool = True,
    gid: str | None = None
) -> list[dict[str, Any]]:
    """
    Fetch data from a public Google Sheet as a list of dictionaries.
    
    Args:
        sheet_id: The Google Sheet ID
        tab_name: Optional tab/sheet name within the spreadsheet
        use_cache: Whether to use cached data if available
        
    Returns:
        List of dictionaries where keys are column headers.
        Returns empty list if sheet is not accessible.
    """
    if not sheet_id:
        return []
    
    cache_key = f"sheet:{sheet_id}:{tab_name or 'default'}"
    
    # Check cache first
    if use_cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    
    # Fetch from Google Sheets
    url = settings.get_sheet_csv_url(sheet_id, tab_name)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=10.0)
            response.raise_for_status()
            
        # Parse CSV
        csv_text = response.text

        reader = csv.DictReader(io.StringIO(csv_text))
        data = list(reader)
        # Cache the result
        cache.set(cache_key, data)
        
        return data
    
    except httpx.HTTPError as e:
        # Log the error but return empty list to allow the app to continue
        print(f"Warning: Could not fetch sheet {sheet_id}: {e}")
        return []



async def get_articles(use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch articles from the articles sheet."""
    return await fetch_sheet_data(settings.sheet_id_articles, use_cache=use_cache)


async def get_boutique(use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch products from the boutique sheet."""
    return await fetch_sheet_data(settings.sheet_id_boutique, use_cache=use_cache)


async def get_church_info(use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch church information from the church_info sheet."""
    return await fetch_sheet_data(settings.sheet_id_church_info, use_cache=use_cache)


async def get_contact(use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch contact submissions from the contact sheet."""
    return await fetch_sheet_data(settings.sheet_id_contact, use_cache=use_cache)


async def get_events(use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch events from the events sheet."""
    return await fetch_sheet_data(settings.sheet_id_events, use_cache=use_cache)


async def get_home_groups(use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch home groups from the home_groups sheet (LR_WEBSITE tab)."""
    return await fetch_sheet_data(
        settings.sheet_id_home_groups, 
        tab_name="LR_WEBSITE",
        use_cache=use_cache
    )


async def get_pastoral_team(use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch pastoral team from the pastoral_team sheet."""
    return await fetch_sheet_data(settings.sheet_id_pastoral_team, use_cache=use_cache)


async def get_services(use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch services from the services sheet."""
    return await fetch_sheet_data(settings.sheet_id_services, use_cache=use_cache)


async def get_vision(use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch vision content from the vision sheet."""
    return await fetch_sheet_data(settings.sheet_id_vision, use_cache=use_cache)
